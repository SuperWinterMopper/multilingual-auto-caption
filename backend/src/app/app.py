from pathlib import Path
from flask import Flask, request
from flask_cors import CORS
import argparse
import multiprocessing
import os
import time
from uuid import UUID, uuid4

from ..components.pipeline_runner import PipelineRunner
from ..components.data_loader import AppDataLoader
from ..components.logger_component import AppLogger
import logging
from silero_vad import load_silero_vad
from speechbrain.inference.classifiers import EncoderClassifier
import torch
from faster_whisper import WhisperModel
from ..dataclasses.inputs.caption import CaptionInput
from ..dataclasses.inputs.caption_status import CaptionStatus
from ..dataclasses.inputs.status import Status


# -----------------------------
# Config
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--prod", action="store_true", help="Run in production mode")

# Under gunicorn, __main__ is not executed; prefer env var for PROD.
# MAC_PROD=1 means prod, MAC_PROD=0 means dev.
PROD = os.environ.get("MAC_PROD", "1") == "1"

app = Flask(__name__)
CORS(app)

# Use a spawn context (safer than fork with torch/cuda/OpenMP stacks).
MP_CTX = multiprocessing.get_context("spawn")

# Globals for a single persistent worker process + queue.
_worker_proc = None
_job_queue = None


# -----------------------------
# Model loaders (used in worker process)
# -----------------------------
def load_asr_model() -> WhisperModel:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch.cuda.is_available() else "float32"
    return WhisperModel("small", device=device, compute_type=compute_type)


def load_slid_model():
    return EncoderClassifier.from_hparams(
        source="speechbrain/lang-id-voxlingua107-ecapa",
        savedir=Path(__file__).parent.parent
        / "pretrained_models"
        / "lang-id-voxlingua107-ecapa",
    )


def load_vad_model():
    return load_silero_vad()


def _worker_main(job_queue: multiprocessing.Queue):
    """
    Long-lived worker process:
    - loads models once
    - processes jobs sequentially
    """
    # Load models ONCE here (most reliable + avoids per-job spikes).
    vad_model = load_vad_model()
    slid_model = load_slid_model()
    asr_model = load_asr_model()

    while True:
        job = job_queue.get()
        if job is None:
            # shutdown sentinel
            break

        job_id_str = job["job_id"]
        payload = job["payload"]
        prod_mode = job["prod_mode"]

        job_id = UUID(job_id_str)

        logger = AppLogger(
            log_suffix=f"job_{job_id_str}", level=logging.INFO, prod=prod_mode
        )
        loader = AppDataLoader(logger=logger, prod=prod_mode)

        try:
            # mark as pending (again) in case caller failed before writing it
            status_obj = CaptionStatus(
                job_id=job_id, status=Status.PENDING, message="Processing started"
            )
            loader.upload_status_file(status_obj)

            input_data = CaptionInput(**payload)

            runner = PipelineRunner(
                file_path=input_data.upload_url,
                vad_model=vad_model,
                slid_model=slid_model,
                asr_model=asr_model,
                convert_to=input_data.convert_to,
                explicit_langs=input_data.explicit_langs,
                prod=prod_mode,
            )

            s3_download_url: str = runner.run(
                caption_color=input_data.caption_color,
                font_size=input_data.font_size,
                stroke_width=input_data.stroke_width,
            )

            status_obj = CaptionStatus(
                job_id=job_id,
                status=Status.COMPLETED,
                output_url=s3_download_url,
                message="Processing completed successfully",
            )
            loader.upload_status_file(status_obj)

        except Exception as e:
            logger.logger.error(f"Job {job_id_str} failed: {e}")
            status_obj = CaptionStatus(
                job_id=job_id, status=Status.FAILED, message=str(e)
            )
            loader.upload_status_file(status_obj)
        finally:
            logger.stop()
            # If you do any local temp files, do cleanup here for prod
            if prod_mode:
                try:
                    loader.cleanup_temp_files()
                except Exception:
                    pass


def _ensure_worker_started():
    """
    Start a single long-lived worker process lazily (on first /caption call).
    Designed for the "I only need 1–2 users" scenario.
    """
    global _worker_proc, _job_queue

    if _worker_proc is not None and _worker_proc.is_alive():
        return

    # (Re)create queue + worker
    _job_queue = MP_CTX.Queue(maxsize=8)  # small queue to avoid runaway memory
    _worker_proc = MP_CTX.Process(target=_worker_main, args=(_job_queue,))
    _worker_proc.daemon = False
    _worker_proc.start()


# -----------------------------
# App mode print
# -----------------------------
if PROD:
    app.config["MODE"] = "prod"
    print("Running in PRODUCTION mode")
else:
    app.config["MODE"] = "dev"
    print("Running in DEVELOPMENT mode")


# -----------------------------
# Routes
# -----------------------------
@app.route("/health", methods=["GET"])
def health_check():
    # NOTE: this only checks the web server, not whether a job is running
    return "OK", 200


@app.route("/presigned", methods=["GET"])
def presigned_s3():
    filename = request.args.get("filename")
    if not filename:
        return '"filename" query parameter is required.', 400

    logger = AppLogger(log_suffix="s3_presign", level=logging.INFO, prod=PROD)
    loader = AppDataLoader(logger=logger, prod=PROD)
    try:
        url = loader.gen_s3_upload_url(filename)
        return url, 200
    except Exception as e:
        logger.logger.error(f"Error generating presigned URL: {str(e)}")
        return f"Error generating presigned URL: {str(e)}", 500
    finally:
        logger.stop()
        if PROD:
            loader.cleanup_temp_files()


@app.route("/caption", methods=["POST"])
def caption():
    try:
        data = request.get_json()
        input_data = CaptionInput(**data)
    except Exception as e:
        return f"Error reading parameters for application: {str(e)}", 400

    job_id = uuid4()

    # Write a "queued/accepted" status immediately so polling works even if worker is booting.
    logger = AppLogger(log_suffix="status_accept", level=logging.INFO, prod=PROD)
    loader = AppDataLoader(logger=logger, prod=PROD)
    try:
        status_obj = CaptionStatus(
            job_id=job_id,
            status=Status.PENDING,
            message="Job accepted and queued",
        )
        loader.upload_status_file(status_obj)
    finally:
        logger.stop()
        if PROD:
            try:
                loader.cleanup_temp_files()
            except Exception:
                pass

    # Start worker if needed and enqueue job as plain dict (avoid pickle issues).
    _ensure_worker_started()
    assert _job_queue is not None

    payload = input_data.model_dump(mode="json")
    try:
        _job_queue.put(
            {"job_id": str(job_id), "payload": payload, "prod_mode": PROD},
            block=False,
        )
    except Exception:
        # Queue full or worker down
        fail_logger = AppLogger(log_suffix="status_reject", level=logging.INFO, prod=PROD)
        fail_loader = AppDataLoader(logger=fail_logger, prod=PROD)
        try:
            status_obj = CaptionStatus(
                job_id=job_id,
                status=Status.FAILED,
                message="Server busy: job queue is full",
            )
            fail_loader.upload_status_file(status_obj)
        finally:
            fail_logger.stop()
        return {"job_id": str(job_id), "message": "Server busy"}, 429

    return {"job_id": str(job_id), "message": "Job accepted and processing started"}, 202


@app.route("/caption/status", methods=["GET"])
def caption_status():
    try:
        if "job_id" not in request.args:
            return "job_id is required", 400

        job_id = UUID(request.args.get("job_id"))

        logger = AppLogger(log_suffix="status_check", level=logging.INFO, prod=PROD)
        loader = AppDataLoader(logger=logger, prod=PROD)

        current_status: CaptionStatus = loader.get_caption_status(job_id)
        logger.stop()

        return current_status.model_dump(by_alias=True, mode="json"), 200
    except Exception as e:
        return f"Error checking status: {str(e)}", 500


if __name__ == "__main__":
    args = parser.parse_args()
    # Local dev only
    PROD = args.prod
    os.environ["MAC_PROD"] = "1" if PROD else "0"
    app.run(host="0.0.0.0", port=5000, debug=not PROD)

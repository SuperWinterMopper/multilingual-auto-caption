from pathlib import Path
from flask import Flask, request
from flask_cors import CORS
import argparse
import threading
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


# read CLI args
parser = argparse.ArgumentParser()
parser.add_argument(
    "--prod",
    action="store_true",
    help="Run the app in production mode (makes it not store large files on disk, just text and image log files)",
)

PROD = False

app = Flask(__name__)
CORS(app)


def load_asr_model() -> WhisperModel:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch.cuda.is_available() else "float32"

    # load model on GPU if available, else cpu
    model = WhisperModel("small", device=device, compute_type=compute_type)
    return model


def load_slid_model():
    return EncoderClassifier.from_hparams(
        source="speechbrain/lang-id-voxlingua107-ecapa",
        savedir=Path(__file__).parent.parent
        / "pretrained_models"
        / "lang-id-voxlingua107-ecapa",
    )


def load_vad_model():
    return load_silero_vad()


# define these globally to avoid re-loading on each request
vad_model = load_vad_model()
slid_model = load_slid_model()
asr_model = load_asr_model()

if PROD:
    app.config["MODE"] = "prod"
    print("Running in PRODUCTION mode")
else:
    app.config["MODE"] = "dev"
    print("Running in DEVELOPMENT mode")


@app.route("/health", methods=["GET"])
def health_check():
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
        print(f"ERROR: {str(e)}")
        logger.logger.error(f"Error generating presigned URL: {str(e)}")
        return f"Error generating presigned URL: {str(e)}", 500
    finally:
        logger.stop()
        if PROD:
            loader.cleanup_temp_files()


def run_background_task(input_data: CaptionInput, job_id: UUID, prod_mode: bool):
    logger = AppLogger(log_suffix="status_worker", level=logging.INFO, prod=prod_mode)
    loader = AppDataLoader(logger=logger, prod=prod_mode)

    try:
        status_obj = CaptionStatus(
            job_id=job_id, status=Status.PENDING, message="Processing started"
        )
        loader.upload_status_file(status_obj)

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
        # Note: pipeline_runner.run returns s3_download_url which might be tuple (bucket, key) or url string?
        # data_loader.save_captioned_s3 returns (bucket, key).
        # pipeline_runner.run calls save_captioned_s3.
        # Let's check pipeline_runner.run return type.
        loader.upload_status_file(status_obj)

    except Exception as e:
        logger.logger.error(f"Job {job_id} failed: {e}")
        status_obj = CaptionStatus(job_id=job_id, status=Status.FAILED, message=str(e))
        loader.upload_status_file(status_obj)
    finally:
        logger.stop()


@app.route("/caption", methods=["POST"])
def caption():
    try:
        data = request.get_json()
        input_data = CaptionInput(**data)
        print(f"Received caption request with data: {data}")
    except Exception as e:
        return f"Error reading parameters for application: {str(e)}", 400

    job_id: UUID = uuid4()

    thread = threading.Thread(
        target=run_background_task, args=(input_data, job_id, PROD)
    )
    thread.daemon = True
    thread.start()

    return {
        "job_id": str(job_id),
        "message": "Job accepted and processing started",
    }, 202


@app.route("/caption/status", methods=["GET"])
def caption_status():
    try:
        data = request.get_json()
        if not data or "job_id" not in data:
            return f"job_id is required, not in json: {data}", 400

        input_status = CaptionStatus(**data)
        job_id = str(input_status.job_id)

        logger = AppLogger(log_suffix="status_check", level=logging.INFO, prod=PROD)
        loader = AppDataLoader(logger=logger, prod=PROD)

        current_status: CaptionStatus = loader.get_caption_status(job_id)
        logger.stop()

        return current_status.model_dump(by_alias=True, mode="json"), 200
    except Exception as e:
        return f"Error checking status: {str(e)}", 500


if __name__ == "__main__":
    args = parser.parse_args()
    PROD = args.prod
    app.run(host="0.0.0.0", port=5000, debug=not PROD)

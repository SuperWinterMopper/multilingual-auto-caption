from flask import Flask, request
from flask_cors import CORS
import argparse
from ..components.pipeline_runner import PipelineRunner
from ..components.data_loader import AppDataLoader
from ..components.logger_component import AppLogger
import logging
from silero_vad import load_silero_vad
from speechbrain.inference.classifiers import EncoderClassifier
import torch
from faster_whisper import WhisperModel
from ..dataclasses.inputs.caption import CaptionInput

# read CLI args
parser = argparse.ArgumentParser()
parser.add_argument('--prod', action='store_true', help='Run the app in production mode (makes it not store large files on disk, just text and image log files)')

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
    return EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")

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
        return "\"filename\" query parameter is required.", 400
    
    logger = AppLogger(log_suffix='s3_presign', level=logging.INFO, prod=PROD)
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

@app.route("/caption", methods=["POST"])
def caption():
    try:
        data = request.get_json()
        input = CaptionInput(**data)
        print(f"Received caption request with data: {data}")
    except Exception as e:
        return f"Error reading parameters for application: {str(e)}", 400

    try:
        runner = PipelineRunner(
            file_path=input.upload_url,
            vad_model=vad_model, 
            slid_model=slid_model, 
            asr_model=asr_model, 
            convert_to=input.convert_to,
            explicit_langs=input.explicit_langs,
            prod=PROD
        )

        # caption_color is a hex string like "#FFFFFF"
        s3_download_url = runner.run(
            caption_color=input.caption_color, 
            font_size=input.font_size, 
            stroke_width=input.stroke_width
        )
        
        print(f"Finished upload job, video saved to {s3_download_url}")
        return { "downloadUrl": s3_download_url }, 200
    except Exception as e:
        print(f"Error processing /caption upload: {str(e)}")
        return f"Error processing upload: {str(e)}", 500
    
if __name__ == "__main__":
    args = parser.parse_args()
    PROD = args.prod
    app.run(host="0.0.0.0", port=5000, debug=not PROD)
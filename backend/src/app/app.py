from flask import Flask, request
import os
import argparse
from ..components.pipeline_runner import PipelineRunner
from ..components.data_loader import AppDataLoader
from ..components.logger import AppLogger
import logging
from silero_vad import load_silero_vad
from speechbrain.inference.classifiers import EncoderClassifier
import torch
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

# read CLI args
parser = argparse.ArgumentParser()
parser.add_argument('--prod', action='store_true', help='Run the app in production mode (makes it not store large files on disk, just text and image log files)')
args = parser.parse_args()
PROD = args.prod

app = Flask(__name__)

def load_asr_model() -> WhisperModel:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch.cuda.is_available() else "float32"

    # load model on GPU if available, else cpu
    model = WhisperModel("large-v3", device=device, compute_type=compute_type)
    return model
        
def load_slid_model():
    return EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")

def load_vad_model():
    return load_silero_vad()
    
# define these globally to avoid re-loading on each request
vad_model = load_vad_model()
slid_model = load_slid_model()
asr_model = load_asr_model()
translate_model = GoogleTranslator()

if args.prod:
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
        return "Error generating presigned URL", 500
    finally:
        logger.stop()
        if PROD:
            loader.cleanup_temp_files()

@app.route("/caption", methods=["POST"])
def caption():
    upload_url = ""
    try:
        data = request.get_json()
        print(f"Received caption request with data: {data}")
        upload_url = data.get("uploadUrl", "")
        assert upload_url != ""
    except Exception as e:
        return f"Error reading required uploadUrl parameter: {str(e)}", 400
    try:
        runner = PipelineRunner(file_path=upload_url, vad_model=vad_model, slid_model=slid_model, asr_model=asr_model, translate_model=translate_model, prod=PROD)
        
        s3_download_url = runner.run()
        
        print(f"Finished upload job, video saved to {s3_download_url}")
        return { "downloadUrl": s3_download_url }, 200
    except Exception as e:
        print(f"Error processing /caption upload: {str(e)}")
        return f"Error processing upload: {str(e)}", 500
    
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
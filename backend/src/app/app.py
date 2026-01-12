from flask import Flask, request
import argparse
from ..components.pipeline_runner import PipelineRunner
from ..components.data_loader import AppDataLoader
from ..components.logger import AppLogger
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
        return "Error generating presigned URL", 500
    finally:
        logger.stop()
        if PROD:
            loader.cleanup_temp_files()

@app.route("/caption", methods=["POST"])
def caption():
    """
    Process a video to add captions/subtitles.
    
    Request Body (JSON):
        upload_url (str, required): The S3 presigned URL or key of the uploaded video file.
        
        captionColor (str, optional): Hex color code for caption text. 
            Default: "#FFFFFF" (white)
            Example: "#FF0000" (red), "#00FF00" (green)
        
        fontSize (int, optional): Font size in pixels for caption text.
            Default: 48
            Range: Typically 24-96 depending on video resolution
        
        strokeWidth (int, optional): Width of the text outline/stroke in pixels.
            Default: 4
            Set to 0 for no outline
        
        convertTo (str, optional): ISO 639-1 language code to translate captions to.
            Default: "" (no translation, keep original language)
            Examples: "en" (English), "ja" (Japanese), "es" (Spanish)
        
        explicitLangs (list[str], optional): List of ISO 639-1 language codes to 
            explicitly specify the languages present in the video. Useful when 
            automatic language detection may be inaccurate.
            Default: [] (auto-detect languages)
            Example: ["en", "es"] for a video with English and Spanish speech
    
    Returns:
        200: JSON with downloadUrl containing presigned S3 URL to download the captioned video
             Example: {"downloadUrl": "https://s3.amazonaws.com/..."}
        400: Error reading required upload_url parameter
        500: Error processing the video
    
    Example Request:
        POST /caption
        Content-Type: application/json
        {
            "upload_url": "https://bucket.s3.amazonaws.com/uploads/2026_01_06.mp4",
            "caption_color": "#FFD700",
            "font_size": 56,
            "stroke_width": 3,
            "convert_to": "en",
            "explicit_langs": ["fr", "it"]
        }
    """
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
    app.run()
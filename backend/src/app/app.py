from flask import Flask, request
import os
import argparse
from ..components.pipeline_runner import PipelineRunner
from ..components.data_loader import AppDataLoader
from ..components.logger import AppLogger
import logging

# read CLI args
parser = argparse.ArgumentParser()
parser.add_argument('--prod', action='store_true', help='Run the app in production mode (makes it not store large files on disk, just text and image log files)')
args = parser.parse_args()
PROD = args.prod

app = Flask(__name__)

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
        url = loader.gen_s3_presigned_url(filename)
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
        runner = PipelineRunner(file_path=upload_url, prod=PROD)
        
        runner.run()
                
        print("Finished upload job")
        return "File uploaded successfully.", 200
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return f"Error processing upload: {str(e)}", 500
    
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
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

app = Flask(__name__)

if args.prod:
    app.config["MODE"] = "prod"
    print("Running in PRODUCTION mode")
else:
    app.config["MODE"] = "dev"
    print("Running in DEVELOPMENT mode")
    
@app.route("/presigned", methods=["GET"])
def presigned_s3(): 
    filename = request.args.get("filename")
    if not filename:
        return "\"filename\" query parameter is required.", 400
    
    logger = AppLogger(log_prefix='s3_presign', level=logging.INFO, prod=(app.config["MODE"] == "prod"))
    loader = AppDataLoader(logger=logger, prod=(app.config["MODE"] == "prod"))
    try:
        url = loader.gen_s3_presigned_url(filename)
        return url, 200
    except Exception as e:
        return "Error generating presigned URL", 500
    finally:
        logger.stop()

@app.route("/caption", methods=["POST"])
def upload():
    if "file_path" not in request.files:
        return "File field missing from request.", 400
    
    runner = PipelineRunner(prod=(app.config["MODE"] == "prod"))
    
    # requried to stop logging
    runner.logger.stop()
    
    print("Finished upload job")
    
    return "File uploaded successfully.", 200
    
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
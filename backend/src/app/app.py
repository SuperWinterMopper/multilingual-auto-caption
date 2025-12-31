from flask import Flask, request
import os
import argparse
from ..components.pipeline_runner import PipelineRunner
from .data_loader import AppDataLoader

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
    
@app.route("/uploads/presigned", methods=["GET"])
def presigned_s3():
    url = AppDataLoader.gen_s3_presigned_url()
    return url, 200

@app.route("/caption", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "File field missing from request.", 400
    
    runner = PipelineRunner(prod=(app.config["MODE"] == "prod"))
    
    print("Finished upload job")
    
    return "File uploaded successfully.", 200
    
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
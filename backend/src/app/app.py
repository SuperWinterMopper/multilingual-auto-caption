from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory, flash
import os
from ..components.runner import AppRunner

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file part in the request.", "error")
        return "File field missing from request.", 400
    
    runner = AppRunner()
    
    print("Finished upload job")
    
    return "File uploaded successfully.", 200
    
    # if not allowed_file(file.filename):
    #     flash("Unsupported file type.", "error")
    #     return redirect(url_for("index"))

    # safe_name = secure_filename(file.filename)
    # dest = unique_name(UPLOAD_DIR / safe_name)
    # file.save(dest)
    # flash(f"Uploaded: {dest.name}", "success")
    # return redirect(url_for("index"))

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
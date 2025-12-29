from pathlib import Path
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev")  # set a strong secret in prod

ROOT_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm", "flv", "mpeg"}

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Upload Video</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; }
    .container { max-width: 720px; margin: 0 auto; }
    .messages { color: #b00; margin-bottom: 1rem; }
    .files { margin-top: 2rem; }
    .file-item { margin: 0.25rem 0; }
    .success { color: #060; }
    form { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
    input[type="file"] { max-width: 100%; }
    button { padding: 0.5rem 0.9rem; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Upload a Video</h1>

    {% with msgs = get_flashed_messages(with_categories=true) %}
      {% if msgs %}
        <div class="messages">
          {% for cat, msg in msgs %}
            <div class="{{ cat }}">{{ msg }}</div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <form method="post" action="{{ url_for('upload') }}" enctype="multipart/form-data">
      <input type="file" name="file" accept="video/*" required />
      <button type="submit">Upload</button>
    </form>

    <div class="files">
      <h2>Uploaded Files</h2>
      {% if files %}
        {% for f in files %}
          <div class="file-item">
            <a href="{{ url_for('serve_upload', filename=f) }}" target="_blank">{{ f }}</a>
          </div>
        {% endfor %}
      {% else %}
        <p>No files uploaded yet.</p>
      {% endif %}
    </div>
  </div>
</body>
</html>
"""

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def unique_name(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    for i in range(1, 10_000):
        candidate = dest.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
    ts = int(time.time())
    return dest.with_name(f"{stem}-{ts}{suffix}")

@app.get("/")
def index():
    files = sorted([p.name for p in UPLOAD_DIR.iterdir() if p.is_file()])
    return render_template_string(TEMPLATE, files=files)

@app.post("/upload")
def upload():
    if "file" not in request.files:
        flash("No file part in the request.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Unsupported file type.", "error")
        return redirect(url_for("index"))

    safe_name = secure_filename(file.filename)
    dest = unique_name(UPLOAD_DIR / safe_name)
    file.save(dest)
    flash(f"Uploaded: {dest.name}", "success")
    return redirect(url_for("index"))

@app.get("/uploads/<path:filename>")
def serve_upload(filename: str):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
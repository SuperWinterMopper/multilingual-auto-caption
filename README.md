# Multilingual Auto Caption

Multilingual Auto Caption is a backend-first service that automatically generates accurate captions for videos containing mixed languages. It combines voice activity detection (VAD), language identification (SLID), and automatic speech recognition (ASR) to produce time-aligned captions and a processed video output with burned-in captions.

This repository contains the backend API, worker pipeline, and a small Next.js frontend used for file uploads and email notifications.

**Project structure (high level)**

- `backend/` — Core application: Flask API, long-lived worker process, pipeline orchestration, S3 integration, and tests.
- `frontend/multilingual-auto-caption/` — Next.js frontend used for uploading videos, polling job status, and requesting email notifications (lightweight).
- `models/` — Model definitions and packaging helpers used by the pipeline.

**Quick links**
- Backend app entry: [backend/src/app/app.py](backend/src/app/app.py)
- Frontend upload helper: [frontend/multilingual-auto-caption/lib/upload-handler.ts](frontend/multilingual-auto-caption/lib/upload-handler.ts)
- Frontend email API route: [frontend/multilingual-auto-caption/app/api/email/route.ts](frontend/multilingual-auto-caption/app/api/email/route.ts)

--

## Backend Overview

The backend is the primary component of this project. It exposes a minimal HTTP API for uploads and job management, and performs captioning work in a separate long-lived worker process to avoid repeated model loading.

Key responsibilities:
- Generate presigned S3 upload URLs for clients to PUT large video files.
- Accept captioning jobs (POST) which enqueue work and immediately return a job ID.
- Provide job status polling so clients can track progress and retrieve final results.
- Run the captioning pipeline (VAD → language ID → ASR → caption rendering) inside a worker process which keeps models loaded for performance.

Core models and libraries used:
- VAD: `silero_vad` (voice activity detection)
- Language identification (SLID): `speechbrain/lang-id-voxlingua107-ecapa`
- ASR: `faster_whisper` (Whisper model)

Worker design:
- A single, lazily-started, long-lived worker process is created via Python `multiprocessing` (spawn context).
- The worker loads heavy models once on start and processes jobs sequentially from a bounded queue (to prevent memory runaway).
- Jobs are enqueued as plain dicts to avoid pickle compatibility issues.

Status handling and storage:
- The app writes status files (Queued → Pending → Completed/Failed) so clients can poll and see progress.
- Output URL (final processed video) is provided as an S3 URL when the job completes.

--

## HTTP API (important endpoints)

- `GET /health` — basic health check for the web server.

- `GET /presigned?filename=<name>` — requests a presigned S3 upload URL for the given filename. The frontend PUTs the file directly to S3 using the returned URL.

- `POST /caption` — starts a captioning job. Expects a JSON payload describing the input and caption rendering options. Returns `job_id` and HTTP 202 when accepted.

- `GET /caption/status?job_id=<uuid>` — fetch current job status. Returns JSON describing `PENDING`, `COMPLETED`, or `FAILED` and includes `output_url` when finished.

See implementation: [backend/src/app/app.py](backend/src/app/app.py)

--

## Typical flow (frontend ↔ backend)

1. Client requests a presigned upload URL from `/presigned` and PUTs the video to S3.
2. Client calls `/caption` with a payload referring to the uploaded file (the backend may accept the full signed URL or a clean S3 path depending on configuration).
3. Backend enqueues the job, returns a `job_id`, and writes an initial status file.
4. The backend worker processes the job, uploads the processed video to S3, and writes a completed status (including `output_url`).
5. Client polls `/caption/status` with the `job_id` to learn when processing is finished and to retrieve the download URL.

--

## Environment & Configuration

Production/dev toggle:
- The backend looks at the environment variable `MAC_PROD` (set to `1` by default in containerized deployments). When running locally you can toggle this via the `--prod` flag or by setting the env var.

Relevant environment variables (backend & deployment):
- AWS credentials for S3 access (standard AWS environment variables or shared credentials file)
- `MAC_PROD` — `1` or `0` to select production behavior

Frontend email API (Next.js) requires SMTP configuration via environment variables:
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, optionally `SMTP_FROM_NAME` and `SMTP_REPLY_TO`.

--

## Development: running backend locally

Requirements:
- Python 3.12 (see CI config), `pip` or `uv`/`pipx` usage referenced in CI
- System dependencies for audio processing (ffmpeg, libsndfile, sox) when running pipeline components locally

Basic steps (local dev):

1. Install Python deps (use your preferred virtualenv):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the Flask app for local development:

```bash
cd backend
python -m src.app.app --help   # see flags
python -m src.app.app          # runs on 0.0.0.0:5000 by default
```

3. Use tools in `src/tests/` for integration tests; CI shows how we run them inside Docker.

--

## Docker & CI

This repository includes a Dockerfile for the backend and a GitHub Actions workflow that builds, runs integration tests, and pushes the image to Amazon ECR. See: `.github/workflows/test-build-backend.yaml` for the CI process.

Example from CI (local mimic): build and run container exposing port 5000, mounting `~/.aws` for credentials:

```bash
cd backend
docker build -t multilingual-auto-caption .
docker run --rm -p 5000:5000 -v ~/.aws:/home/app/.aws:ro -e AWS_SHARED_CREDENTIALS_FILE=/home/app/.aws/credentials multilingual-auto-caption
```

--

## Frontend (brief)

The repository contains a minimal Next.js frontend used to obtain presigned upload URLs, PUT videos to S3, call `/caption`, poll `/caption/status`, and request an email with the download link. The upload logic lives in `frontend/multilingual-auto-caption/lib/upload-handler.ts` and the email API route in `frontend/multilingual-auto-caption/app/api/email/route.ts`.

The frontend is intentionally lightweight — the backend performs the heavy lifting of model inference and file processing.

--

## Troubleshooting & logs

- Server logs and per-job logs are written by `AppLogger` (see backend components). Integration test logs are kept under `backend/logs/` in CI runs.
- If the worker fails to start or the queue is full, the API returns `429` with a message that the server is busy.

--

## Contributing

If you plan to add models or processing stages, please:
- Keep heavy model loads inside the worker process to avoid per-request spikes.
- Add tests under `backend/src/tests` and update CI if new native dependencies are required.

--

If you'd like, I can also add a short `backend/README.md` with developer-focused run and debug instructions, or add example cURL commands and a sample `env` file. Want me to add those next?


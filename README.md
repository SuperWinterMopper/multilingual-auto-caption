# Multilingual Auto Caption

Multilingual Auto Caption automatically generates accurate captions for videos containing mixed languages. It combines voice activity detection (VAD), language identification (SLID), and automatic speech recognition (ASR) to produce time-aligned captions and a processed video output with burned-in captions.

This repository contains the backend API, worker pipeline, and a Next.js frontend used for file uploads and email notifications.

# Examples
![korean translated](frontend/multilingual-auto-caption/public/ko_trans.png)
![korean translated](frontend/multilingual-auto-caption/public/ja2en.png)

**Project structure (high level)**

- `backend/` — Core application: Flask API, long-lived worker process, pipeline orchestration, S3 integration, and tests.
- `frontend/multilingual-auto-caption/` — Next.js frontend used for uploading videos, polling job status
- `models/` — Model definitions and packaging helpers used by the pipeline.

## Backend Overview

It exposes a minimal HTTP API for uploads and job management, and performs captioning work in a separate long-lived worker process to avoid repeated model loading. Files are stored on S3


## HTTP API (important endpoints)

- `GET /health` — basic health check for the web server.

- `GET /presigned?filename=<name>` — requests a presigned S3 upload URL for the given filename. The frontend PUTs the file directly to S3 using the returned URL.

- `POST /caption` — starts a captioning job. Expects a JSON payload describing the input and caption rendering options. Returns `job_id` and HTTP 202 when accepted.

- `GET /caption/status?job_id=<uuid>` — fetch current job status. Returns JSON describing `PENDING`, `COMPLETED`, or `FAILED` and includes `output_url` when finished.


## Configuration
Relevant environment variables (backend & deployment):
- AWS credentials for S3 access (standard AWS environment variables or shared credentials file)
- `MAC_PROD` — `1` or `0` to select production mode

Frontend environment variables necessary:
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, optionally `SMTP_FROM_NAME` and `SMTP_REPLY_TO`.


## Development: running backend locally

Requirements:
- Python 3.12 (see CI config), `pip` or `uv`/`pipx` usage referenced in CI
- System dependencies for audio processing (ffmpeg, libsndfile, sox) when running pipeline components locally

Basic steps (local dev):

1. Install dependencies:

```bash
cd backend
uv venv
uv run pip install .
```

2. Run the Flask app for local development:

```bash
cd backend
python -m src.app.app --help   # see flags
python -m src.app.app          # runs on 0.0.0.0:5000 by default
```

## Docker & CI

This repository includes a Dockerfile for the backend and a GitHub Actions workflow that builds, runs integration tests, and pushes the image to Amazon ECR. See: `.github/workflows/test-build-backend.yaml` for the CI process.


```bash
cd backend
docker build -t multilingual-auto-caption .
docker run --rm -p 5000:5000 -v ~/.aws:/home/app/.aws:ro -e AWS_SHARED_CREDENTIALS_FILE=/home/app/.aws/credentials multilingual-auto-caption
```

--

## Frontend

The repository contains a minimal Next.js frontend used to obtain presigned upload URLs, PUT videos to S3, call `/caption`, poll `/caption/status`, and request an email with the download link. The upload logic lives in `frontend/multilingual-auto-caption/lib/upload-handler.ts` and the email API route in `frontend/multilingual-auto-caption/app/api/email/route.ts`.

## Troubleshooting & logs

- Server logs and per-job logs are written by `AppLogger` (see backend components). Integration test logs are kept under `backend/logs/` in CI runs.
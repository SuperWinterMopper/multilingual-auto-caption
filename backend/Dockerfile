FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsndfile1 libsox-dev sox git build-essential python3-dev portaudio19-dev curl

RUN pip install uv

COPY pyproject.toml uv.lock* ./

# will break at runtime if you create a virtualenv in docker 
ENV UV_SYSTEM_PYTHON=1

RUN uv sync --frozen

COPY . .
RUN useradd -m app
RUN mkdir -p /app
RUN chown -R app:app /app /home/app
USER app

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "2", "-b", "0.0.0.0:5000", "src.app.app:app"]

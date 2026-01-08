FROM python:3.13-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y ffmpeg libsndfile1  libsox-dev sox git build-essential python3-dev portaudio19-dev

RUN pip install poetry

COPY . .

RUN poetry install

ENV UPLOAD_BUCKET=multilingual-auto-caption

EXPOSE 5000

RUN useradd app
USER app

CMD ["poetry", "run", "python", "-m", "src.app.app", "--prod"]
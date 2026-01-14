FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsndfile1 libsox-dev sox git build-essential python3-dev portaudio19-dev

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

# will break at runtime if you create a virtualenv in docker 
ENV POETRY_VIRTUALENVS_CREATE=false 

RUN poetry install

COPY . .

RUN useradd app
RUN chown -R app:app /app
USER app

EXPOSE 5000
    
CMD ["python", "-m", "src.app.app", "--prod"]
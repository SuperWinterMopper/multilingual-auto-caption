export UPLOAD_BUCKET := multilingual-auto-caption

setup:
	echo "UPLOAD_BUCKET: $(UPLOAD_BUCKET)"

run-dev: setup
	uv run gunicorn -w 2 -k gthread --threads 2 -b 0.0.0.0:5000 src.app.app:app

run-prod: setup 
	uv run python -m src.app.app --prod

test-pipe:
	uv run pytest -s -k test_pipe_full

print-last-logs:
	uv run python -m src.tests.print_last_log

docker-build:
	docker build -t multilingual-auto-caption .

docker-run:
	docker run -d -p 5000:5000 -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) -e UPLOAD_BUCKET=$(UPLOAD_BUCKET) --name captioner multilingual-auto-caption

docker-stop:
	docker stop multilingual-auto-caption:latest

test-temp:
	uv run python -m src.tests.temp
export UPLOAD_BUCKET := multilingual-auto-caption

setup:
	echo "UPLOAD_BUCKET: $(UPLOAD_BUCKET)"

run-dev: setup
	poetry run python -m src.app.app

run-prod: setup 
	poetry run python -m src.app.app --prod

test-pipe-local:
	poetry run pytest -s -k test_pipe_local

test-pipe-docker:
	poetry run pytest -s -k test_pipe_docker

docker-build:
	docker build -t multilingual-auto-caption .

docker-run:
	docker run -d -p 5000:5000 -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) -e UPLOAD_BUCKET=$(UPLOAD_BUCKET) --name captioner multilingual-auto-caption

docker-stop:
	docker stop multilingual-auto-caption:latest

test-temp:
	poetry run python -m src.tests.temp
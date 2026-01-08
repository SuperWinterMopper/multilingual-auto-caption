export UPLOAD_BUCKET := multilingual-auto-caption

setup:
	echo "UPLOAD_BUCKET: $(UPLOAD_BUCKET)"

run-dev: setup
	poetry run python -m src.app.app

run-prod: setup 
	poetry run python -m src.app.app --prod

test-pipe: setup
	make run-prod & sleep 360 && poetry run pytest -s -k test_pipeline_updated

test-vis: setup
	poetry run pytest -s -k test_log_segments_visualization

test-parse: setup
	poetry run pytest -s -k test_parse_prediction

test-trans: setup
	poetry run pytest -s src/tests/test_translate.py

docker-build:
	docker build -t multilingual-auto-caption .

docker-run:
	docker run -d -p 5000:5000 -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) -e UPLOAD_BUCKET=$(UPLOAD_BUCKET) --name captioner multilingual-auto-caption

docker-stop:
	docker stop multilingual-auto-caption:latest
export UPLOAD_BUCKET := multilingual-auto-caption

setup:
	echo "UPLOAD_BUCKET: $(UPLOAD_BUCKET)"

run-dev: setup
	poetry run python -m src.app.app

test: setup
	poetry run pytest -s src/tests
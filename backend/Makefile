export UPLOAD_BUCKET := multilingual-auto-caption

setup:
	echo "UPLOAD_BUCKET: $(UPLOAD_BUCKET)"

run-dev: setup
	poetry run python -m src.app.app

test-pipe: setup
	poetry run pytest -s -k test_pipeline

test-vis: setup
	poetry run pytest -s -k test_log_segments_visualization

test-parse: setup
	poetry run pytest -s -k test_parse_prediction

test-trans: setup
	poetry run pytest -s src/tests/test_translate.py
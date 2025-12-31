setup:
	export UPLOAD_BUCKET=multilingual-auto-caption && echo "UPLOAD_BUCKET set" 

run-dev: setup
	poetry run python -m src.app.app

test: setup
	poetry run pytest -s src/tests
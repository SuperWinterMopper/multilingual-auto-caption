# this is for sagemaker initial setup
sagemaker-init:
	sudo apt update
	sudo apt install tree ffmpeg
	pip install poetry 
	poetry install
	poetry env info

test-all:
	poetry run python -m pytest

test-vad:
	poetry run python -m pytest -s tests/test_VADPipeline.py tests/test_melspecpipeline.py

test-slid:
	poetry run python -m pytest -s tests/test_SLIDPipeline.py 

upload-vad-data:
	poetry run python src/common/data_controller.py -m VAD -r src/VAD/data --upload

download-vad-data:
	poetry run python src/common/data_controller.py -m VAD -r src/VAD/data

train-vad:
	poetry run python src/VAD/training/train_runner.py
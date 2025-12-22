test-all:
	poetry run python -m pytest

test-vad:
	poetry run python -m pytest -s tests/test_VADPipeline.py tests/test_melspecpipeline.py

test-slid:
	poetry run python -m pytest -s tests/test_SLIDPipeline.py 

upload-vad-data:
	poetry run python src/common/data_controller.py -m VAD -r src/VAD/data --upload
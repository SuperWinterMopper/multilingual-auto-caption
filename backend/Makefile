run-dev:
	poetry run python -m flask --app src.app.app run

upload:
	poetry run pytest src/tests

test-presigned:
	curl -X GET http://localhost:5000/uploads/presigned
	
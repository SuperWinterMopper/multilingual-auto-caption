import requests
from pathlib import Path

UPLOAD_URL = "http://localhost:5000/upload"
JAPANESE_TEST_FILE_PATH = Path(__file__).parent / "files" / "japanese.mp3"

def test_integration_client():
    payload = {"file": open(JAPANESE_TEST_FILE_PATH, "rb")}
    response = requests.post(UPLOAD_URL, files=payload)
    assert response.status_code == 200
    print(f"Test successful, response: {response.text}")
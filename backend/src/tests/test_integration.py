import requests
from pathlib import Path

BASE_URL = "http://localhost:5000"
PRESIGNED_URL = BASE_URL + "/presigned"
JAPANESE_TEST_FILE_PATH = Path(__file__).parent / "files" / "japanese.mp3"

def test_presigned():
    response = requests.get(PRESIGNED_URL, params={"filename": str(JAPANESE_TEST_FILE_PATH.name)})
    assert response.status_code == 200, f"Presigned URL request failed with status text {response.text}"
    print(f"Presigned test successful, response: {response.text}")
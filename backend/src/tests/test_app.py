import requests
from pathlib import Path

BASE_URL = "http://localhost:5000"
PRESIGNED_URL = BASE_URL + "/presigned"
TEST_FILE_PATH = Path(__file__).parent / "files" / "test.MOV"

def test_health():
    response = requests.get(BASE_URL + "/health")
    assert response.status_code == 200, f"Health check failed with status text {response.text}"
    print("Health check successful")

def test_presigned():
    response = requests.get(PRESIGNED_URL, params={"filename": str(TEST_FILE_PATH.name)})
    assert response.status_code == 200, f"Presigned URL request failed with status text {response.text}"
    print(f"Presigned test successful, response: {response.text}")
    
    # Parse response
    data = response.json()
    upload_url = data["uploadUrl"]
    bucket = data["bucket"]
    key = data["key"]
    
    # Upload file to S3
    with open(TEST_FILE_PATH, "rb") as f:
        upload_response = requests.put(
            upload_url,
            data=f,
            headers={"Content-Type": "video/quicktime"},
            timeout=300
        )
    
    assert upload_response.status_code == 200, f"S3 upload failed with status {upload_response.status_code}: {upload_response.text}"
    print(f"File successfully uploaded to s3://{bucket}/{key}")
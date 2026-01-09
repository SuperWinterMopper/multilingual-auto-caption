import pytest
import requests
from pathlib import Path
from ..app.app import app

# Test file paths
TEST_FILES = Path(__file__).parent / "files"
TEST_FILE_PATH = TEST_FILES / "test.MOV"
FRENCH_TEST_FILE_PATH = TEST_FILES / "french.mp4"
HINDI_TEST_FILE_PATH = TEST_FILES / "hindi.mp4"
JAPANESE_TEST_FILE_PATH = TEST_FILES / "japanese.mp4"
PORTUGUESE_TEST_FILE_PATH = TEST_FILES / "portuguese.mp4"
SPANISH_TEST_FILE_PATH = TEST_FILES / "spanish.mp4"
KOREAN_TEST_FILE_PATH = TEST_FILES / "korean.mp4"


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("video_path,caption_color,font_size,stroke_width,explicitLangs,convert_to", [
    pytest.param(TEST_FILE_PATH, "#FFFFFF", 48, 4, [], "", id="japanese and english-"),
    pytest.param(KOREAN_TEST_FILE_PATH, "#9B1919", 48, 4, ["zh"], "", id="korean-to-chinese"),
    pytest.param(KOREAN_TEST_FILE_PATH, "#FFFFFF", 48, 4, ["fa"], "", id="korean-to-farsi"),
    pytest.param(KOREAN_TEST_FILE_PATH, "#52FF77", 48, 4, ["de"], "", id="korean-to-german"),
    # pytest.param(SPANISH_TEST_FILE_PATH, "#FFFFFF", 48, 6, ["es"], "fr", id="spanish-to-french"),
    # pytest.param(HINDI_TEST_FILE_PATH, "#2539FF", 80, 4, [], "", id="hindi-blue-captions"),
    # pytest.param(FRENCH_TEST_FILE_PATH, "#FFD700", 36, 2, [], "en", id="french-to-english"),
    # pytest.param(PORTUGUESE_TEST_FILE_PATH, "#FFFFFF", 48, 4, [], "en", id="portuguese-defaults"),
    # pytest.param(KOREAN_TEST_FILE_PATH, "#FFFFFF", 96, 4, [], "en", id="korean-to-english"),
])

def test_pipeline_updated(client, video_path, caption_color, font_size, stroke_width, explicitLangs, convert_to):
    """Test the full captioning pipeline with various video inputs and styling options."""
    print(f"Testing pipeline with file: {video_path.name}")
    
    response = client.get("/presigned", query_string={"filename": video_path.name})
    assert response.status_code == 200, f"Presigned URL request failed with status text {response.text}"
    print(f"Presigned test successful, response: {response.text}")
    
    data = response.get_json()
    upload_url = data["uploadUrl"]
    bucket = data["bucket"]
    key = data["key"]
    
    with open(video_path, "rb") as f:
        upload_response = requests.put(
            upload_url,
            data=f,
            headers={"Content-Type": "video/mp4"},
            timeout=300
        )
    
    assert upload_response.status_code == 200, f"S3 upload failed with status {upload_response.status_code}: {upload_response.text}"
    print(f"File successfully uploaded to s3://{bucket}/{key}")
    
    caption_response = client.post(
        "/caption",
        json={
            "uploadUrl": upload_url,
            "captionColor": caption_color,
            "fontSize": font_size,
            "strokeWidth": stroke_width,
            "convertTo": convert_to,
            "explicitLangs": explicitLangs
        },
    )

    assert caption_response.status_code == 200, f"Caption request failed with status {caption_response.status_code}: {caption_response.text}"
    print(f"Caption request accepted for {upload_url}")
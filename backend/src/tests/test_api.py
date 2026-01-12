from pydantic import AnyHttpUrl
import pytest
import requests
from pathlib import Path
from ..app.app import app
from ..dataclasses.inputs.caption import CaptionInput
import requests

# Test file paths
TEST_FILES = Path(__file__).parent / "files"
JAP_ENG_TEST_FILE_PATH = TEST_FILES / "jap-eng2.mp4"
FRENCH_TEST_FILE_PATH = TEST_FILES / "french.mp4"
HINDI_TEST_FILE_PATH = TEST_FILES / "hindi.mp4"
JAPANESE_TEST_FILE_PATH = TEST_FILES / "japanese.mp4"
PORTUGUESE_TEST_FILE_PATH = TEST_FILES / "portuguese.mp4"
SPANISH_TEST_FILE_PATH = TEST_FILES / "spanish.mp4"
KOREAN_TEST_FILE_PATH = TEST_FILES / "korean.mp4"
ARABIC_TEST_FILE_PATH = TEST_FILES / "arabic.mp4"

# Placeholder URL for test cases (will be replaced with actual presigned URL)
PLACEHOLDER_URL = AnyHttpUrl("https://example.com/placeholder")

DOCKER_BACKEND = "http://localhost:5000"

@pytest.fixture(scope="session")
def backend(request):
    return request.config.getoption("--backend")
    
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("video_path,caption_input", [
    pytest.param(
        JAP_ENG_TEST_FILE_PATH,
        CaptionInput(upload_url=PLACEHOLDER_URL),
        id="japanese and english"
    ),
    pytest.param(
        KOREAN_TEST_FILE_PATH,
        CaptionInput(upload_url=PLACEHOLDER_URL, caption_color="#9B1919", explicit_langs=["ko"], convert_to="zh"),
        id="korean-to-chinese"
    ),
    pytest.param(
        ARABIC_TEST_FILE_PATH,
        CaptionInput(upload_url=PLACEHOLDER_URL, caption_color="#886CA1", font_size=12, stroke_width=10, convert_to="ja"),
    )
])

def test_pipe_full(backend, client, video_path, caption_input: CaptionInput):
    """Test the full captioning pipeline with various video inputs and styling options."""
    print(f"Testing pipeline with file: {video_path.name}")
    
    assert backend in ['local', 'docker'], f"Invalid backend specified: {backend}, must be either local or docker"
    TEST_ON_DOCKER = backend == 'docker'
    
    print(f"Backend is {backend}")
    
    if not TEST_ON_DOCKER:
        response = client.get("/presigned", query_string={"filename": video_path.name})
        data = response.get_json()
    elif TEST_ON_DOCKER:
        response = requests.get(DOCKER_BACKEND + "/presigned", params={"filename": video_path.name})
        data = response.json()
    else:
        raise ValueError("Invalid backend specified")

    assert response.status_code == 200, f"Presigned URL request failed with status text {response.text}"
    print(f"Presigned test successful, response: {response.text}")
    
    upload_url = data["upload_url"]
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
    
    # Update the upload_url with the actual presigned URL and serialize to dict
    caption_input_dict = caption_input.model_dump(by_alias=True)
    caption_input_dict["upload_url"] = upload_url
    
    if not TEST_ON_DOCKER:
        caption_response = client.post(
            "/caption",
            json=caption_input_dict,
        )
    elif TEST_ON_DOCKER:
        caption_response = requests.post(
            DOCKER_BACKEND + "/caption",
            json=caption_input_dict,
        )
    else:
        raise ValueError("Invalid backend specified")

    assert caption_response.status_code == 200, f"Caption request failed with status {caption_response.status_code}: {caption_response.text}"
    print(f"Caption request accepted for {upload_url}")
from pydantic import AnyHttpUrl
import pytest
import requests
import time
from pathlib import Path
from uuid import uuid4
import logging


from ..app.app import app
from ..dataclasses.inputs.caption import CaptionInput
from ..dataclasses.inputs.caption_status import CaptionStatus
from ..dataclasses.inputs.status import Status
from ..components.data_loader import AppDataLoader
from ..components.logger_component import AppLogger

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
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "video_path,caption_input",
    [
        pytest.param(
            KOREAN_TEST_FILE_PATH,
            CaptionInput(
                upload_url=PLACEHOLDER_URL,
                caption_color="#9B1919",
                explicit_langs=["ko"],
                convert_to="zh",
            ),
            id="korean-to-chinese",
        ),
    ],
)
def test_pipe_full(backend, client, video_path, caption_input: CaptionInput):
    """Test the full captioning pipeline with various video inputs and styling options."""
    print(f"Testing pipeline with file: {video_path.name}")

    assert backend in ["local", "docker"], (
        f"Invalid backend specified: {backend}, must be either local or docker"
    )
    TEST_ON_DOCKER = backend == "docker"

    print(f"Backend is {backend}")

    if not TEST_ON_DOCKER:
        response = client.get("/presigned", query_string={"filename": video_path.name})
        data = response.get_json()
    elif TEST_ON_DOCKER:
        response = requests.get(
            DOCKER_BACKEND + "/presigned", params={"filename": video_path.name}
        )
        breakpoint()
        data = response.json()
    else:
        raise ValueError("Invalid backend specified")

    assert response.status_code == 200, (
        f"Presigned URL request failed with status text {response.text}"
    )
    print(f"Presigned test successful, response: {response.text}")

    try:
        upload_url = data["upload_url"]
        bucket = data["bucket"]
        key = data["key"]
    except KeyError as e:
        raise KeyError(f"Missing expected key in presigned URL response: {e}")

    with open(video_path, "rb") as f:
        upload_response = requests.put(
            upload_url, data=f, headers={"Content-Type": "video/mp4"}, timeout=300
        )

    assert upload_response.status_code == 200, (
        f"S3 upload failed with status {upload_response.status_code}: {upload_response.text}"
    )
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

    assert caption_response.status_code == 202, (
        f"Caption request failed with status {caption_response.status_code}: {caption_response.text}"
    )

    job_data = (
        caption_response.get_json() if not TEST_ON_DOCKER else caption_response.json()
    )
    job_id = job_data["job_id"]
    print(f"Caption request accepted for {upload_url}, job_id: {job_id}")

    # Poll for status
    status = Status.PENDING
    start_time = time.time()
    # Wait up to 10 minutes
    while (
        status in [Status.PENDING, Status.UNINITIATED]
        and time.time() - start_time < 600
    ):
        time.sleep(5)
        print(f"Polling status for job {job_id}...")

        if not TEST_ON_DOCKER:
            status_response = client.get("/caption/status", json={"job_id": job_id})
        else:
            status_response = requests.get(
                DOCKER_BACKEND + "/caption/status", json={"job_id": job_id}
            )

        if status_response.status_code != 200:
            print(f"Status check failed: {status_response.text}")
            continue

        status_data = (
            status_response.get_json() if not TEST_ON_DOCKER else status_response.json()
        )
        status = Status(status_data.get("status"))
        print(
            f"============Status report for job {job_id}: {status_data}================="
        )

    assert status == Status.COMPLETED, f"Job failed to complete. Final status: {status}"


def test_s3_status_upload_download():
    """Test looking up and saving status to S3 without running the pipeline."""
    # This requires AWS credentials to be set up in the environment
    logger = AppLogger(log_suffix="test_status", level=logging.INFO)
    loader = AppDataLoader(logger=logger)

    job_id = uuid4()

    # 1. Create a status object
    status_obj = CaptionStatus(
        job_id=job_id, status=Status.PENDING, message="Test pending message"
    )

    # 2. Upload it
    print(f"Uploading status for job {job_id}")
    loader.upload_status_file(status_obj)

    # 3. Retrieve it
    retrieved_status: CaptionStatus = loader.get_caption_status(job_id)
    print(f"Retrieved status: {retrieved_status}")

    assert retrieved_status is not None
    assert retrieved_status.status == Status.PENDING
    assert retrieved_status.message == "Test pending message"
    assert retrieved_status.job_id == job_id

    # 4. Update it
    status_obj.status = Status.COMPLETED
    status_obj.message = "Test completed"
    status_obj.output_url = "http://example.com/result.mp4"

    loader.upload_status_file(status_obj)

    # 5. Retrieve again
    retrieved_status_2: CaptionStatus = loader.get_caption_status(job_id)

    assert retrieved_status_2.status == Status.COMPLETED
    assert retrieved_status_2.output_url == "http://example.com/result.mp4"

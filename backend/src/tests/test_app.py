import requests
from pathlib import Path
from moviepy import VideoFileClip
import torch

from ..components.logger import AppLogger
from ..dataclasses.audio_segment import AudioSegment

BASE_URL = "http://localhost:5000"
TEST_FILES = Path(__file__).parent / "files"
PRESIGNED_URL = BASE_URL + "/presigned"
TEST_FILE_PATH = TEST_FILES / "test.MOV"
FRENCH_TEST_FILE_PATH = TEST_FILES / "french.mp4"
HINDI_TEST_FILE_PATH = TEST_FILES / "hindi.mp4"
JAPANESE_TEST_FILE_PATH = TEST_FILES / "japanese.mp4"
PORTUGUESE_TEST_FILE_PATH = TEST_FILES / "portuguese.mp4"
SPANISH_TEST_FILE_PATH = TEST_FILES / "spanish.mp4"
KOREAN_TEST_FILE_PATH = TEST_FILES / "korean.mp4"

def test_health():
    response = requests.get(BASE_URL + "/health")
    assert response.status_code == 200, f"Health check failed with status text {response.text}"
    print("Health check successful")

def test_pipeline():
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
    
    # Kick off captioning with the uploaded object
    caption_response = requests.post(
        url=BASE_URL + "/caption",
        json={"uploadUrl": upload_url},
    )

    assert caption_response.status_code == 200, f"Caption request failed with status {caption_response.status_code}: {caption_response.text}"
    print(f"Caption request accepted for {upload_url}")


def test_log_segments_visualization():
    """Test the log_segments_visualization method with sample audio segments."""
    # Initialize logger
    logger = AppLogger(log_suffix="test_segments_viz", prod=False)
    
    # Load video
    video = VideoFileClip(str(TEST_FILE_PATH))
    
    # Create audio segments with specified time ranges and languages
    # 2 segments with "English", 1 segment with "Spanish"
    segment_data = [
        {'start': 1.4, 'end': 4.7, 'lang': 'Japanese'},
        {'start': 6.0, 'end': 8.3, 'lang': 'English'},
        {'start': 10.5, 'end': 12.55, 'lang': 'English'}
    ]
    
    audio_segments = []
    dummy_audio = torch.zeros(int(video.duration * 16000), dtype=torch.float32)
    for data in segment_data:
        # Create a dummy audio tensor (1 second of silence at 16kHz as placeholder)
        audio_segments.append(AudioSegment(
            audio=dummy_audio,
            start_time=data['start'],
            end_time=data['end'],
            lang=data['lang'],
            orig_file=TEST_FILE_PATH.name,
            sample_rate=16000 if not video.audio else int(video.audio.fps)
        ))
    
    logger.log_segments_visualization(log_prefix="test", video=video, audio_segments=audio_segments)
    
    video.close()
    logger.stop()
    
    print("log_segments_visualization test completed successfully. Check under /logs for the visualization image.")
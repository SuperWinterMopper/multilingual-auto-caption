import requests
from pathlib import Path
from moviepy import VideoFileClip
import torch
from speechbrain.inference.classifiers import EncoderClassifier
from ..components.slid_model import SLIDModel
from ..components.vad_model import VADModel
from ..components.asr_model import ASRModel
from ..components.logger import AppLogger
from ..dataclasses.audio_segment import AudioSegment
from ..components.video_processor import VideoProcessor
from silero_vad import load_silero_vad
from moviepy import VideoFileClip, CompositeVideoClip
from faster_whisper import WhisperModel 
import torch
from datetime import datetime

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

def create_dummy_audio_segments(video: VideoFileClip) -> list[AudioSegment]:
    audio_segments = []
    # Create audio segments with specified time ranges and languages
    # 2 segments with "English", 1 segment with "Spanish"
    segment_data = [
        {'start': 1.4, 'end': 4.7},
        {'start': 6.0, 'end': 8.3},
        {'start': 10.5, 'end': 12.55}
    ]
    dummy_audio = torch.zeros(int(16000), dtype=torch.float32)
    for data in segment_data:
        # Create a dummy audio tensor (1 second of silence at 16kHz as placeholder)
        audio_segments.append(AudioSegment(
            audio=dummy_audio,
            start_time=data['start'],
            end_time=data['end'],
            orig_file=TEST_FILE_PATH.name,
            sample_rate=16000 if not video.audio else int(video.audio.fps)
        ))
    return audio_segments

def test_health():
    response = requests.get(BASE_URL + "/health")
    assert response.status_code == 200, f"Health check failed with status text {response.text}"
    print("Health check successful")

def test_pipeline():
    files_to_test = [
        FRENCH_TEST_FILE_PATH,
        HINDI_TEST_FILE_PATH,
        JAPANESE_TEST_FILE_PATH,
        PORTUGUESE_TEST_FILE_PATH,
        SPANISH_TEST_FILE_PATH,
        KOREAN_TEST_FILE_PATH
    ]
    
    for test_file in files_to_test:
        print(f"Testing pipeline with file: {test_file.name}")
        
        # Step 1: Get presigned URL
        response = requests.get(PRESIGNED_URL, params={"filename": str(test_file.name)})
        assert response.status_code == 200, f"Presigned URL request failed with status text {response.text}"
        print(f"Presigned test successful, response: {response.text}")
        
        # Parse response
        data = response.json()
        upload_url = data["uploadUrl"]
        bucket = data["bucket"]
        key = data["key"]
        
        # Upload file to S3
        with open(test_file, "rb") as f:
            upload_response = requests.put(
                upload_url,
                data=f,
                headers={"Content-Type": "video/mp4"},
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
    video_processor = VideoProcessor(logger=logger, prod=False)
    
    sr, audio_tensor = video_processor.extract_audio(video, allowed_sample_rates=[16000])
    
    audio_segments = create_dummy_audio_segments(video)
    
    logger.log_segments_visualization(log_prefix="test", video=video, audio_segments=audio_segments)
    
    video.close()
    logger.stop()
    
    print("log_segments_visualization test completed successfully. Check under /logs for the visualization image.")
    
def setup():
    # Initialize logger
    logger = AppLogger(log_suffix="testing", prod=False)
    
    # Load models as done in app.py
    vad_model_silero = load_silero_vad()
    slid_model_sb = EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")
    
    # Instantiate component models
    vad_model = VADModel(model=vad_model_silero, logger=logger, prod=False)
    video_processor = VideoProcessor(logger=logger, prod=False)
    slid_model = SLIDModel(model=slid_model_sb, logger=logger, prod=False)
    asr_model = ASRModel(logger=logger, model=load_asr_model(), prod=False)
    
    # Load video
    video = VideoFileClip(str(TEST_FILE_PATH))
    
    # Extract audio with proper resampling to SLIDModel's allowed sample rates
    sample_rate, audio_tensor = video_processor.extract_audio(video, slid_model.allowed_sample_rates)
    
    # Detect speech segments using VAD
    speech_timestamps = vad_model.detect_speech(audio_tensor, sample_rate)
    
    # Create audio segments from speech timestamps
    audio_segments = video_processor.segment_audio(
        audio_tensor=audio_tensor,
        segments=speech_timestamps,
        sample_rate=sample_rate,
        orig_file=TEST_FILE_PATH.name
    )
    
    # Run classify_segments_language which internally uses parse_prediction
    audio_segments = slid_model.classify_segments_language(audio_segments)
    
    audio_segments = video_processor.chunk_segments(audio_segments)
    logger.log_segments_visualization(
        log_prefix="chunked_classified", 
        video=video, 
        audio_segments=audio_segments
    )
    
    audio_segments = asr_model.transcribe_segments(audio_segments)
    logger.log_transcription_results(
        audio_segments=audio_segments, 
        log_prefix="transcribed"
    )
    
    return audio_segments, logger, video, video_processor

def test_embed_captions():
    audio_segments, logger, video, video_processor = setup()
    
    # Now test embed_captions
    composite_clip: CompositeVideoClip = video_processor.embed_captions(video, audio_segments)
    
    # Save the resulting video with embedded captions for manual verification
    output_path = Path(f"./temp_embed_test_embed_captions_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    composite_clip.write_videofile(str(output_path))
    
    composite_clip.close()
    
    video.close()
    logger.stop()
    
    print(f"embed_captions test completed successfully. Output saved to {output_path}")
    
def load_asr_model() -> WhisperModel:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch.cuda.is_available() else "float32"

    # load model on GPU if available, else cpu
    model = WhisperModel("large-v3", device=device, compute_type=compute_type)
    return model

def test_asr_transcription():
    print('Loading ASR model...')
    model = load_asr_model()
    print('Model loaded. Transcribing sample file...')
    files = [(JAPANESE_TEST_FILE_PATH, 'ja'), (PORTUGUESE_TEST_FILE_PATH, 'pt')]
    
    temp_output = TEST_FILES / "temp_transcriptions"
    temp_output.mkdir(exist_ok=True)
    
    for file_path, lang in files:
        print(f'Transcribing file: {file_path.name} with language code: {lang}...')
        segments, info = model.transcribe(
            str(file_path), 
            language=lang,
            word_timestamps=True
        )
        
        output = temp_output / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        print(f"Finished for {file_path.name}, writing transcription to file {output}...")
        with open(output, "a", encoding="utf-8") as f:
            for segment in segments:
                f.write(f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}\n")
            f.write(f"\nInfo\n{info}\n")    
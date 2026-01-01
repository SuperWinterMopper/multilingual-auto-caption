from .logger import AppLogger
from silero_vad import load_silero_vad, get_speech_timestamps
import torch

class VADModel():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.logger.logger.info('VADModel initialized')
        self.model = load_silero_vad()
    
    def detect_speech(self, audio_tensor: torch.Tensor, sample_rate: int) -> list:
        try:
            self.logger.logger.info(f'Starting VAD processing')
            speech_timestamps = get_speech_timestamps(
                audio=audio_tensor,
                model=self.model,
                sampling_rate=sample_rate,
                return_seconds=True
            )
            log_speech_max_length = 10 # how many segments to log
            
            self.logger.logger.info(f"Detected {len(speech_timestamps)} speech segments: {speech_timestamps[:log_speech_max_length]}{'...' if len(speech_timestamps) > log_speech_max_length else ''}")
            return speech_timestamps
        
        except Exception as e:
            self.logger.logger.error(f"Error during VAD processing: {str(e)}")
            raise
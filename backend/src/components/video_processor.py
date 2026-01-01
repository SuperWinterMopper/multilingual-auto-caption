from .logger import AppLogger
from moviepy import VideoFileClip
import torch

class VideoProcessor():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.logger.logger.info('VideoProcessor initialized')
    
    def extract_audio(self, video: VideoFileClip) -> tuple[int, torch.Tensor]:
        try:
            if video.audio is None:
                raise ValueError("Video has no audio track")
            
            # Extract audio as numpy array
            # audio_array shape: (n_samples, n_channels) or (n_samples,) for mono
            audio_array = video.audio.to_soundarray()
            
            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio_array).float()
            
            # If stereo, convert to mono by averaging channels
            if audio_tensor.ndim == 2:
                audio_tensor = audio_tensor.mean(dim=1)
                self.logger.logger.debug(f"Converted stereo audio to mono for {video.filename}")
            else:
                self.logger.logger.debug(f"Video audio is already mono for {video.filename}")
            
            self.logger.logger.info(f"Extracted audio: shape={audio_tensor.shape}, sample_rate={video.audio.fps}")
            
            return video.audio.fps, audio_tensor
            
        except Exception as e:
            self.logger.logger.error(f"Error extracting audio from video: {str(e)}")
            raise
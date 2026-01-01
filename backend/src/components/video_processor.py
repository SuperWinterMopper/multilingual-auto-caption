from .logger import AppLogger
from moviepy import VideoFileClip
import torch
from bisect import bisect_right
import torchaudio.transforms as T

class VideoProcessor():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.logger.logger.info('VideoProcessor initialized')
        
    def extract_audio(self, video: VideoFileClip, allowed_sample_rates: list[int]) -> tuple[int, torch.Tensor]:
        try:
            if video.audio is None:
                raise ValueError("Video has no audio track")
            
            if not allowed_sample_rates:
                raise ValueError("allowed_sample_rates cannot be empty")
            
            # Extract audio as numpy array, audio_array  shape: (n_samples, n_channels) or (n_samples,) for mono
            audio_array = video.audio.to_soundarray()

            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio_array).float()
            
            if audio_tensor.ndim == 2:
                audio_tensor = audio_tensor.mean(dim=1)  # Convert to mono by averaging channels
                self.logger.logger.debug(f"Converted stereo audio to mono for {video.filename}")
            else:
                self.logger.logger.debug(f"Video audio is already mono for {video.filename}")
            
            # Resample if necessary
            original_sample_rate = video.audio.fps
            allowed_sample_rates.sort()
            target_sample_rate_ind = max(bisect_right(allowed_sample_rates, original_sample_rate) - 1, 0)
            target_sample_rate = allowed_sample_rates[target_sample_rate_ind]            

            if original_sample_rate != target_sample_rate:
                audio_tensor = T.Resample(orig_freq=original_sample_rate, new_freq=target_sample_rate)(audio_tensor)
                
                self.logger.logger.info(f"Resampled audio from {original_sample_rate} Hz to {target_sample_rate} Hz for {video.filename}")
            
            self.logger.logger.info(f"Extracted audio: shape={audio_tensor.shape}, sample_rate={target_sample_rate}")
            
            return target_sample_rate, audio_tensor
            
        except Exception as e:
            self.logger.logger.error(f"Error extracting audio from video: {str(e)}")
            raise
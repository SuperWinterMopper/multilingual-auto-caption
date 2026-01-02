from .logger import AppLogger
from moviepy import VideoFileClip
import torch
from bisect import bisect_right
import torchaudio.transforms as T
from ..dataclasses.audio_segment import AudioSegment
import math
import numpy as np

class VideoProcessor():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.logger.logger.info('VideoProcessor initialized')
        self.max_caption_duration = 3 # maximum length any 1 subtitle is on screen
        
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
    
    def segment_audio(self, audio_tensor: torch.Tensor, segments: list[dict[str, float]], sample_rate: int, orig_file: str) -> list[AudioSegment]:
        result = []
        assert audio_tensor.ndim == 1, "Audio tensor must be mono"
        try:
            for segment in segments:
                start_time = segment['start']
                end_time = segment['end']
                
                start_idx = int(start_time * sample_rate)
                end_idx = int(end_time * sample_rate)
                
                audio_segment = audio_tensor[start_idx:end_idx]
                
                result.append(AudioSegment(
                    audio=audio_segment,
                    start_time=start_time,
                    end_time=end_time,
                    orig_file=orig_file,
                    sample_rate=sample_rate
                ))
        except Exception as e:
            self.logger.logger.error(f"Error segmenting audio: {str(e)}")
            raise
        
        assert len(result) == len(segments), "Number of audio segments does not match number of segments"
        self.logger.logger.info(f"Segmented audio into {len(result)} segments for file {orig_file}")
        return result
        
    def chunk_segments(self, audio_segments: list[AudioSegment]) -> list[AudioSegment]:
        assert all(seg.audio.ndim == 1 for seg in audio_segments), "All audio segments must be mono"
        self.logger.logger.info(f"Chunking {len(audio_segments)} audio segments with max duration {self.max_caption_duration} seconds")
        
        def chunk_segment(seg: AudioSegment) -> list[AudioSegment]:
            try:
                duration = seg.end_time - seg.start_time
                num_chunks = int(math.ceil(duration / self.max_caption_duration))
                chunks = []
                for chunk in range(num_chunks):
                    start_idx = int((chunk * self.max_caption_duration) * seg.sample_rate)
                    end_idx = int(((chunk + 1) * self.max_caption_duration) * seg.sample_rate)
                    
                    start_time = seg.start_time + chunk * self.max_caption_duration
                    end_time = min(seg.start_time + (chunk + 1) * self.max_caption_duration, seg.end_time)
                    
                    chunk_audio = seg.audio[start_idx:end_idx]
                    chunks.append(AudioSegment(
                        audio=chunk_audio,
                        start_time=start_time,
                        end_time=end_time,
                        orig_file=seg.orig_file,
                        sample_rate=seg.sample_rate,
                        lang=seg.lang,
                    ))
                return chunks
            except Exception as e:
                self.logger.logger.error(f"Error chunking segment {seg.id}: {str(e)}")
                raise
    
        new_segments = []
        for seg in audio_segments:
            chunked = chunk_segment(seg)
            assert chunked[0].start_time == seg.start_time, "Chunking altered start time"
            assert chunked[-1].end_time == seg.end_time, "Chunking altered end time"
            
            # extra checking only in dev mode
            if not self.prod:
                assert sum(c.audio.numel() for c in chunked) == seg.audio.numel(), "Chunking altered total audio samples"
                assert np.isclose(sum(c.end_time - c.start_time for c in chunked), (seg.end_time - seg.start_time)), "Chunking altered total duration"
            new_segments.extend(chunked)
        
        self.logger.logger.info(f"Finished chunking into {len(new_segments)} segments from {len(audio_segments)} original segments")
        return new_segments
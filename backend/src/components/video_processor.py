from pydantic import AnyHttpUrl
from .logger import AppLogger
from .data_loader import AppDataLoader
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import torch
from bisect import bisect_right
import torchaudio.transforms as T
from ..dataclasses.audio_segment import AudioSegment, unknown_language, unknown_text
import math
import numpy as np
from fontTools.ttLib import TTFont
from PIL import ImageFont

class VideoProcessor():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.logger.logger.info('VideoProcessor initialized')
        self.max_caption_duration = 6 # maximum length any 1 subtitle is on screen
        
        self.fonts = [str(font_path) for font_path in AppDataLoader.get_avail_fonts()]
        
        # only in dev mode, check all fonts are legal for TextClip
        if not self.prod:
            for font in self.fonts:
                try:
                    _ = ImageFont.truetype(font)
                except Exception as e:
                    raise ValueError(
                        "During initialization of VideoProcessor, error with font {}, pillow failed to use it with error {}".format(
                            font, e
                        )
                    )
        
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
    
    def segment_audio(self, audio_tensor: torch.Tensor, segments: list[dict[str, float]], sample_rate: int, orig_file: AnyHttpUrl) -> list[AudioSegment]:
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
                    orig_file=orig_file.unicode_string(),
                    sample_rate=sample_rate,
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
    
    def pick_font_for_text(self, text: str) -> str:
        def font_supports_text(font_path: str, text: str) -> bool:
            if not text: # if text is empty any font will do
                self.logger.logger.warning(f"Text is empty so deeming font is valid for text:<{text}> at {font_path}")
                return True
            try:
                tt = TTFont(font_path)
                cmap = set()
                for table in tt["cmap"].tables:
                    cmap.update(table.cmap.keys())
                return all(ord(ch) in cmap or ch.isspace() for ch in text)
            except Exception as e:
                self.logger.logger.error(f"Error occured in font_supports_text: {e}. Deeming that ")
                return True
        try:
            for font_path in self.fonts:
                if font_supports_text(font_path, text):
                    return font_path
        except Exception as e:
            self.logger.logger.error(f"Error in main loop for pick_font_for_text: {e}")
            raise
        
        # if no fonts work :(
        default_choice = self.fonts[0]
        self.logger.logger.warning(f"No font found that supports all characters in text: {text[:50]}. Defaulting to {default_choice}.")
        return default_choice
    
    # caption_color is a hex string like  "#FFFFFF"
    def embed_captions(self, video: VideoFileClip, audio_segments: list[AudioSegment], caption_color: str, font_size: int, stroke_width: int) -> CompositeVideoClip:
        if video is None:
            raise ValueError("video object is None - video retrieval may have failed")
        if audio_segments is None:
            raise ValueError("audio_segments is None - audio processing may have failed")
        
        # Debug logging for None checks
        self.logger.logger.info(f"embed_captions called with video={video}, audio_segments type={type(audio_segments)}, len={len(audio_segments)}")
        
        
        self.logger.logger.info(f"Embedding {len(audio_segments)} captions ({audio_segments[0].text}...) into video {video.filename}")
        
        assert all(seg.end_time <= video.duration for seg in audio_segments), "All audio segments must have end time within video duration"
        assert all(seg.lang != unknown_language for seg in audio_segments), "All segments must have known language before embedding captions"
        assert all(seg.text != unknown_text for seg in audio_segments), "All segments must have known text before embedding captions"
        
        text_clips = []
        
        try:
            for seg in audio_segments:
                duration = seg.end_time - seg.start_time
                
                if seg.text == '' or seg.text is None:
                    continue
                
                try:
                    txt_clip = TextClip(
                        text=seg.text,
                        method='caption',
                        size=(int(video.w * 0.8), None),
                        font=self.pick_font_for_text(seg.text),
                        font_size=font_size,
                        color=caption_color,
                        stroke_color="black",
                        stroke_width=stroke_width,
                        margin=(10, 10),
                    )
                    
                    txt_clip = txt_clip.with_start(seg.start_time).with_duration(duration)
                except Exception as e:
                    self.logger.logger.error(f"Error occured in indiviaul TextClip creation: {e}")
                    raise
                
                # Position text so its bottom edge is 8% from video bottom
                bottom_margin = int(video.h * 0.08)
                y_position = video.h - txt_clip.h - bottom_margin
                txt_clip = txt_clip.with_position(('center', max(0, y_position)))
                
                text_clips.append(txt_clip)
        except Exception as e:
            self.logger.logger.error(f"Error occured during creation of TextClips for embedding into video: {e}")
            raise
        
        try:
            final_video = CompositeVideoClip([video] + text_clips, size=(video.w, video.h))
        except Exception as e:
            self.logger.logger.error(f"Error occured during creation of CompositeVideoClip: {e}")
            raise 
        
        self.logger.logger.info(f"Successfully embedded {len(text_clips)} captions into video")
        return final_video
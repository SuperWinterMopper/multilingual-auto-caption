from .logger import AppLogger
from .data_loader import AppDataLoader
from .asr_model import ASRModel
from .vad_model import VADModel
from .slid_model import SLIDModel
from .video_processor import VideoProcessor
import logging

class PipelineRunner():
    def __init__(self, file_path: str, vad_model, slid_model, prod=False):
        self.prod = prod
        self.file_path = file_path
        
        self.logger = AppLogger(log_suffix='pipe', level=logging.INFO, prod=self.prod)
        self.loader = AppDataLoader(logger=self.logger, prod=self.prod)
        self.vad_model = VADModel(model=vad_model, logger=self.logger, prod=self.prod)
        self.slid_model = SLIDModel(model=slid_model, logger=self.logger, prod=self.prod)
        self.asr_model = ASRModel(logger=self.logger, prod=self.prod)
        self.video_processor = VideoProcessor(logger=self.logger, prod=self.prod)
        
        self.logger.logger.info('Runner initialized')
    
    def run(self):
        self.logger.logger.info(f'Starting pipeline for file: {self.file_path}')
        
        video = self.loader.retrieve_video(self.file_path)
        self.logger.logger.info('Video is loaded as variable `video` in PipelineRunner.run(),')
        self.logger.log_video_metrics(video)
        self.logger.log_metrics_snapshot()
        
        sample_rate, audio_tensor = self.video_processor.extract_audio(
            video=video, 
            allowed_sample_rates=self.vad_model.allowed_sample_rates)
        
        voiced_segments = self.vad_model.detect_speech(audio_tensor, sample_rate)
        
        # break up tensor into audio segments
        audio_segments = self.video_processor.segment_audio(
            audio_tensor=audio_tensor,
            segments=voiced_segments,
            sample_rate=sample_rate,
            orig_file=self.file_path
        )
        self.logger.log_segments_visualization(
            log_prefix="init", 
            video=video, 
            audio_segments=audio_segments
        )
        
        # classify each segment's language
        audio_segments = self.slid_model.classify_segments_language(audio_segments)
        self.logger.log_segments_visualization(
            log_prefix="classified", 
            video=video, 
            audio_segments=audio_segments
        )
        
        # chunk segments to max caption duration
        audio_segments = self.video_processor.chunk_segments(audio_segments)
        self.logger.log_segments_visualization(
            log_prefix="chunked_classified", 
            video=video, 
            audio_segments=audio_segments
        )
        
        print(f"Finished language identification for {len(audio_segments)} segments for NOW")
        
        # requried to stop logging
        self.logger.stop()
        
        # don't delete files if in dev mode
        if self.prod:
            self.loader.cleanup_temp_files()

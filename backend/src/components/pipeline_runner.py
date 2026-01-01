from .logger import AppLogger
from .data_loader import AppDataLoader
from .asr_model import ASRModel
from .vad_model import VADModel
from .slid_model import SLIDModel
from .video_processor import VideoProcessor
import logging

class PipelineRunner():
    def __init__(self, file_path: str, prod=False):
        self.prod = prod
        self.file_path = file_path
        
        self.logger = AppLogger(log_prefix='pipe_run', level=logging.INFO, prod=self.prod)
        self.loader = AppDataLoader(logger=self.logger, prod=self.prod)
        self.vad_model = VADModel(logger=self.logger, prod=self.prod)
        self.slid_model = SLIDModel(logger=self.logger, prod=self.prod)
        self.asr_model = ASRModel(logger=self.logger, prod=self.prod)
        self.video_processor = VideoProcessor(logger=self.logger, prod=self.prod)
        
        self.logger.logger.info('Runner initialized')
    
    def run(self):
        self.logger.logger.info(f'Starting pipeline for file: {self.file_path}')
        
        video = self.loader.retrieve_video(self.file_path)
        self.logger.logger.info('Video is loaded as variable `video` in PipelineRunner.run(),')
        self.logger.log_video_metrics(video)
        self.logger.log_metrics_snapshot()
        
        sample_rate, audio_tensor = self.video_processor.extract_audio(video)
        segments = self.vad_model.detect_speech(audio_tensor, sample_rate)
        
        print(f"segments: {segments}")
        
        
        
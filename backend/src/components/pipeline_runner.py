from .logger import AppLogger
from .data_loader import AppDataLoader
from .asr_model import ASRModel
from .vad_model import VADModel
from .slid_model import SLIDModel
from .video_processor import VideoProcessor, CompositeVideoClip
import logging

class PipelineRunner():
    def __init__(self, file_path: str, vad_model, slid_model, asr_model,prod=False):
        self.prod = prod
        self.file_path = file_path
        
        self.logger = AppLogger(log_suffix='pipe', level=logging.INFO, prod=self.prod)
        self.loader = AppDataLoader(logger=self.logger, prod=self.prod)
        self.vad_model = VADModel(model=vad_model, logger=self.logger, prod=self.prod)
        self.slid_model = SLIDModel(model=slid_model, logger=self.logger, prod=self.prod)
        self.asr_model = ASRModel(logger=self.logger, model=asr_model, prod=self.prod)
        self.video_processor = VideoProcessor(logger=self.logger, prod=self.prod)
        
        self.allowed_sample_rates = self.consolidate_sample_rates([
            self.vad_model.allowed_sample_rates,
            self.asr_model.allowed_sample_rates,
            self.slid_model.allowed_sample_rates
        ])
        
        self.logger.logger.info('Runner initialized')
    
    def run(self):
        self.logger.logger.info(f'Starting pipeline for file: {self.file_path}')
        
        video = self.loader.retrieve_video(self.file_path)
        self.logger.logger.info('Video is loaded as variable `video` in PipelineRunner.run(),')
        self.logger.log_video_metrics(video)
        self.logger.log_metrics_snapshot()
        
        sample_rate, audio_tensor = self.video_processor.extract_audio(
            video=video, 
            allowed_sample_rates=self.allowed_sample_rates
        )
        
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
        
        audio_segments = self.asr_model.transcribe_segments(audio_segments)
        self.logger.log_transcription_results(
            audio_segments=audio_segments, 
            log_prefix="transcribed"
        )
        
        captioned_video: CompositeVideoClip = self.video_processor.embed_captions(video, audio_segments)
        
        output_path = self.loader.save_captioned_disk(captioned_video)
        
        bucket, key = self.loader.save_captioned_s3(video_path=output_path)
        
        self.logger.logger.info("Pipeline finished successfully.")
        
        # requried to stop logging
        self.logger.stop()
        
        # don't delete files if in dev mode
        if self.prod:
            self.loader.cleanup_temp_files()
            
        return output_path

    def consolidate_sample_rates(self, sample_rates: list[list[int]]) -> list[int]:
        consolidated = set(rate for rates in sample_rates for rate in rates)
        return sorted(list(consolidated))
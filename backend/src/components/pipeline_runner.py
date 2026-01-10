from .logger import AppLogger
from .data_loader import AppDataLoader
from .asr_model import ASRModel
from .vad_model import VADModel
from .slid_model import SLIDModel
from .video_processor import VideoProcessor, CompositeVideoClip
from .translater import AppTranslater
import logging
from moviepy import TextClip
from ..dataclasses.audio_segment import AudioSegment
from pydantic import AnyHttpUrl

class PipelineRunner():
    def __init__(self, file_path: AnyHttpUrl, vad_model, slid_model, asr_model, convert_to="", explicit_langs: list[str]=[], prod=False):
        self.prod = prod
        self.file_path = file_path
        
        self.logger = AppLogger(log_suffix='pipe', level=logging.INFO, prod=self.prod)
        self.loader = AppDataLoader(logger=self.logger, prod=self.prod)
        self.vad_model = VADModel(model=vad_model, logger=self.logger, prod=self.prod)
        self.slid_model = SLIDModel(model=slid_model, logger=self.logger, prod=self.prod)
        self.asr_model = ASRModel(logger=self.logger, model=asr_model, prod=self.prod)
        self.translater = AppTranslater(logger=self.logger, prod=self.prod)
        self.video_processor = VideoProcessor(logger=self.logger, prod=self.prod)
        
        self.consolidated_langs = self.consolidate_sample_rates([
            self.vad_model.allowed_sample_rates,
            self.asr_model.allowed_sample_rates,
            self.slid_model.allowed_sample_rates
        ])
        
        # classify each segment's language
        # breakpoint()
        self.allowed_langs = self.consolidate_allowed_langs([
            self.slid_model.get_allowed_langs(),
            self.asr_model.get_allowed_langs(),
            self.translater.get_allowed_langs()
        ])
        
        # if explicit langs are provided, further restrict allowed langs
        if len(explicit_langs) > 0:
            self.logger.logger.info(f"Explicit languages provided: {explicit_langs}, consolidating with existing allowed languages: {self.allowed_langs}")
            self.allowed_langs = self.consolidate_allowed_langs([self.allowed_langs, explicit_langs])
            self.logger.logger.info(f"Explicit languages provided, consolidated allowed languages are now: {self.allowed_langs}")
        
        if self.allowed_langs == []:
            raise ValueError("No allowed languages remain after consolidation. Please check the provided explicit languages.")
        
        # convert all subtitles to this language if provided. otherwise, subtitles remain in their original language
        self.convert_to = convert_to
        assert self.convert_to in self.translater.allowed_langs or self.convert_to == "" or convert_to == "zh", f"Conversion language '{self.convert_to}' is not supported by the translation model"
        
        self.logger.logger.info('Runner initialized')
    
    # caption_color is a hex string like "#FFFFFF"
    def run(self, caption_color="#FFFFFF", font_size=48, stroke_width=4) -> str:
        # validate caption format parameters before running pipeline
        self.validate_caption_format(caption_color, font_size, stroke_width)
        
        self.logger.logger.info(f'Starting pipeline for file: {self.file_path} with allowed langs: {self.allowed_langs} and convert_to: {self.convert_to}')
        
        video, video_path = self.loader.retrieve_video(self.file_path)
        self.logger.logger.info('Video is loaded as variable `video` in PipelineRunner.run(),')
        self.logger.log_video_metrics(video)
        self.logger.log_metrics_snapshot()
    
        sample_rate, audio_tensor = self.video_processor.extract_audio(
            video=video, 
            allowed_sample_rates=self.consolidated_langs
        )
        
        voiced_segments = self.vad_model.detect_speech(audio_tensor, sample_rate)
        
        # break up tensor into audio segments
        audio_segments = self.video_processor.segment_audio(
            audio_tensor=audio_tensor,
            segments=voiced_segments,
            sample_rate=sample_rate,
            orig_file=self.file_path
        )
        
        if not audio_segments:
            bucket, key = self.loader.save_captioned_s3(video_path=video_path)
            s3_download_url = self.loader.gen_s3_download_url(bucket=bucket, key=key)
            return s3_download_url
            
        self.logger.log_segments_visualization(
            log_prefix="init", 
            video=video, 
            audio_segments=audio_segments
        )
        
        audio_segments = self.slid_model.classify_segments_language(
            audio_segments=audio_segments,
            allowed_langs=self.allowed_langs
        )
        audio_segments = self.clean_audio_segments(audio_segments)
        
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
        audio_segments = self.clean_audio_segments(audio_segments)
        
        audio_segments = self.asr_model.transcribe_segments(audio_segments)
        self.logger.log_transcription_results(
            audio_segments=audio_segments, 
            log_prefix="transcribed"
        )
        audio_segments = self.clean_audio_segments(audio_segments)
        
        if self.convert_to != "":
            audio_segments = self.translater.translate_audio_segments(
                audio_segments=audio_segments,
                target_lang=self.convert_to
            )
            self.logger.logger.info("Translated language, logging the new transcription results ")
            self.logger.log_transcription_results(
                audio_segments=audio_segments, 
                log_prefix="transcribed"
            )
            audio_segments = self.clean_audio_segments(audio_segments)

            
        captioned_video: CompositeVideoClip = self.video_processor.embed_captions(
            video, 
            audio_segments, 
            caption_color, 
            font_size, 
            stroke_width
        )
        
        output_path = self.loader.save_captioned_disk(captioned_video)
        
        bucket, key = self.loader.save_captioned_s3(video_path=output_path)
        
        s3_download_url = self.loader.gen_s3_download_url(bucket=bucket, key=key)
        
        self.logger.logger.info("Pipeline finished successfully.")
        
        # requried to stop logging
        self.logger.stop()
        
        # don't delete files if in dev mode
        if self.prod:
            self.loader.cleanup_temp_files()
            
        return s3_download_url
    
    def consolidate_sample_rates(self, sample_rates: list[list[int]]) -> list[int]:
        consolidated = set(rate for rates in sample_rates for rate in rates)
        return sorted(list(consolidated))
    
    def consolidate_allowed_langs(self, allowed_langs_lists: list[list[str]]) -> list[str]:
        self.logger.logger.info(f"Consolidating allowed languages from lists: {allowed_langs_lists}")
        langs_sets = [set(lang_list) for lang_list in allowed_langs_lists]
        
        # special handling for Chinese variants - normalize zh-CN, zh-TW, etc. to 'zh'
        normalized_sets = []
        for lang_set in langs_sets:
            normalized = set()
            for lang in lang_set:
                if lang.startswith("zh"):
                    normalized.add("zh")
                else:
                    normalized.add(lang)
            normalized_sets.append(normalized)
            self.logger.logger.info(f"Normalized lang set: {normalized}")
        
        consolidated_set = set.intersection(*normalized_sets)
        return sorted(list(consolidated_set))

    def validate_caption_format(self, caption_color, font_size, stroke_width):
        try:
            _ = TextClip(
                text="test",
                method='caption',
                size=(100, None),
                font_size=font_size,
                color=caption_color,
                stroke_color="black",
                stroke_width=stroke_width,
                margin=(10, 10))
            
        except Exception as e:
            self.logger.logger.error(f"Caption format validation failed: {str(e)}")
            raise ValueError(f"Invalid caption format parameters: {str(e)}")
    
    def clean_audio_segments(self, audio_segments: list[AudioSegment]):
        for seg in audio_segments:
            if type(seg.text) != type("str"):
                seg.text = ""
        return audio_segments
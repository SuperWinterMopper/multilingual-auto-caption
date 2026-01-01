from .logger import AppLogger
from ..dataclasses.audio_segment import AudioSegment

class SLIDModel():
    def __init__(self, model, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.model = model
        self.model.encoder.ignore_len()  # needed to suppress CategoricalEncoder warning about correct category count
        self.logger.logger.info('SLIDModel initialized')
        
    def classify_segments_language(self, audio_segments: list[AudioSegment]) -> list[AudioSegment]:
        self.logger.logger.info(f"Beginning language classification for {len(audio_segments)} audio segments")
        for seg in audio_segments:
            try:
                prediction = self.model.classify_batch(seg.audio)
                lang_code = prediction[3][0]  # Extract ISO code
                seg.lang = lang_code
            except Exception as e:
                self.logger.logger.error(f"Error classifying language for segment {seg.id}: {str(e)}")
                seg.lang = "ERROR"
        self.logger.logger.info(f"Completed language classification for {len(audio_segments)} audio segments")
        self.logger.log_audio_segments_list(audio_segments)
        return audio_segments
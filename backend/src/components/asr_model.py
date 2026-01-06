from .logger import AppLogger
from ..dataclasses.audio_segment import AudioSegment, unknown_language
from faster_whisper import WhisperModel
from faster_whisper.tokenizer import _LANGUAGE_CODES

class ASRModel():
    def __init__(self, logger: AppLogger, model: WhisperModel, prod=False):
        self.logger = logger
        self.prod = prod
        self.allowed_sample_rates = [16000] # made up for this moment, just matches the other models
        self.model = model
        self.allowed_langs = [str(lang_code) for lang_code in _LANGUAGE_CODES]
        self.logger.logger.info('ASRModel initialized')
    
    def transcribe_segments(self, audio_segments: list[AudioSegment]) -> list[AudioSegment]:
        assert all(seg.lang != unknown_language for seg in audio_segments), "All segments must have a known language before transcription."
        
        def transcribe_segment(seg: AudioSegment) -> AudioSegment:
            segments, info = self.model.transcribe(
                audio=seg.audio.numpy(), 
                language=seg.lang, 
                word_timestamps=True
            )
            seg.text = " ".join([s.text for s in segments]).strip()
            return seg
            
        self.logger.logger.info(f"Beginning transcription for {len(audio_segments)} audio segments")
        transcribed_segments = []
        try:
            for seg in audio_segments:
                trans_seg = transcribe_segment(seg)
                transcribed_segments.append(trans_seg)
                self.logger.logger.debug(f"Segment {trans_seg.id} transcribed with text length {len(trans_seg.text)}")
        except Exception as e:
            self.logger.logger.error(f"Error during transcription: {str(e)}")
            raise
        return transcribed_segments
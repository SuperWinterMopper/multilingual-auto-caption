from .logger import AppLogger
from ..dataclasses.audio_segment import AudioSegment, unknown_language
from faster_whisper import WhisperModel
from faster_whisper.tokenizer import _LANGUAGE_CODES
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        
        def transcribe_segment(idx_seg: tuple[int, AudioSegment]) -> tuple[int, AudioSegment]:
            idx, seg = idx_seg
            segments, info = self.model.transcribe(
                audio=seg.audio.numpy(), 
                language=seg.lang,
                word_timestamps=True
            )
            seg.text = " ".join([s.text for s in segments]).strip() or ""
            
            # debugging, double make sure not None
            if seg.text == None:
                seg.text = ""
            return idx, seg
            
        self.logger.logger.info(f"Beginning transcription for {len(audio_segments)} audio segments")
        try:
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(transcribe_segment, enumerate(audio_segments)))

            # sort to preserve original order
            transcribed_segments = [seg for _, seg in sorted(results, key=lambda x: x[0])]
        except Exception as e:
            self.logger.logger.error(f"Error during transcription: {str(e)}")
            raise
        self.logger.logger.info(f"Completed transcription for {len(audio_segments)} audio segments")
        return transcribed_segments
    
    @classmethod
    def get_allowed_langs(cls) -> list[str]:
        return sorted([str(lang_code) for lang_code in _LANGUAGE_CODES])
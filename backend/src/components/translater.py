from .logger import AppLogger
from deep_translator import GoogleTranslator
from typing import Union
from ..dataclasses.audio_segment import AudioSegment

class AppTranslater:
    def __init__(self, logger: AppLogger, prod=False):
        self.prod = prod
        self.logger = logger
        self.allowed_langs = self.get_allowed_langs(GoogleTranslator().get_supported_languages(as_dict=True))
        self.logger.logger.info('AppTranslater initialized')
        
    def translate_text(self, texts: list[str], source_lang: str, target_lang: str) -> list[str]:
        assert target_lang in self.allowed_langs, f"Target language '{target_lang}' is not supported."
        assert source_lang in self.allowed_langs, f"Source language '{source_lang}' is not supported."
        
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translation = translator.translate_batch(texts)
            return translation
        except Exception as e:
            self.logger.logger.error(f"Error during translation from {source_lang} to {target_lang}: {str(e)}")
            raise
        
    def translate_audio_segments(self, audio_segments: list[AudioSegment], target_lang: str) -> list[AudioSegment]:
        for seg in audio_segments:
            try:
                # Skip if already in target language
                if seg.lang == target_lang:
                    self.logger.logger.debug(f"Segment {seg.id} already in target language '{target_lang}', skipping translation.")
                    continue
                
                # Skip empty text
                if not seg.text or seg.text.strip() == "":
                    self.logger.logger.debug(f"Segment {seg.id} has empty text, skipping translation.")
                    continue
                
                translated_text = self.translate_text(
                    texts=[seg.text],
                    source_lang=seg.lang,
                    target_lang=target_lang
                )[0]
                
                seg.text = translated_text
                seg.lang = target_lang
                
            except Exception as e:
                self.logger.logger.error(f"Error translating segment {seg.id}: {str(e)}")
                raise
        
        return audio_segments
            
    def get_allowed_langs(self, langs: Union[list, dict]) -> list[str]:
        assert isinstance(langs, (dict)), "langs must be a dict"
        return [str(lang_code) for lang_code in langs.values()]
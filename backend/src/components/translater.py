
from .logger import AppLogger
from deep_translator import GoogleTranslator
from typing import Union

class AppTranslater:
    def __init__(self, logger: AppLogger, translate_model: GoogleTranslator, prod=False):
        self.prod = prod
        self.logger = logger
        self.translater = translate_model
        self.allowed_langs = self.get_allowed_langs(self.translater.get_supported_languages(as_dict=True))
        self.logger.logger.info('AppTranslater initialized')
        
    def translate_text(self, text: str, target_lang: str) -> str:
        return ""
        
    def get_allowed_langs(self, langs: Union[list, dict]) -> list[str]:
        assert isinstance(langs, (dict)), "langs must be a dict"
        return [str(lang_code) for lang_code in langs.values()]
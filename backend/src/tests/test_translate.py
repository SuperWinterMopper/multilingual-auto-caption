from ..components.translater import AppTranslater
from ..components.logger import AppLogger
from deep_translator import GoogleTranslator

translate_model = GoogleTranslator()

def test_translate_module():
    logger = AppLogger(log_suffix="test_translate")
    translater = AppTranslater(logger=logger)
    
    txt = ["犬には名前があります。", "あの子は将来学者になるでしょう", "死んでも嫌だ"]
    source_lang = "ja"
    target_lang = "en"
    res = translater.translate_text(txt, source_lang, target_lang)
    
    logger.logger.info(f"Translation results from {source_lang} to {target_lang}: {res}")
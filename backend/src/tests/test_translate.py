from ..components.translater import AppTranslater
from ..components.logger import AppLogger


def test_translate_module():
    logger = AppLogger(log_suffix="test_translate")
    translater = AppTranslater(logger=logger)

    print(translater.allowed_langs)
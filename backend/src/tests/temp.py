from faster_whisper.tokenizer import _LANGUAGE_CODES
from deep_translator import GoogleTranslator

# _LANGUAGE_CODES is a tuple of all supported language codes
print(_LANGUAGE_CODES)

# Test if 'zh' works as a language code
test_text = "Hello, how are you?"

try:
    # Try 'zh' directly
    result = GoogleTranslator(source='en', target='zh').translate(test_text)
    print(f"'zh' works: {result}")
except Exception as e:
    print(f"'zh' failed: {e}")

try:
    # Try 'zh-CN' (Simplified Chinese)
    result = GoogleTranslator(source='en', target='zh-CN').translate(test_text)
    print(f"'zh-CN' works: {result}")
except Exception as e:
    print(f"'zh-CN' failed: {e}")

try:
    # Try 'zh-TW' (Traditional Chinese)
    result = GoogleTranslator(source='en', target='zh-TW').translate(test_text)
    print(f"'zh-TW' works: {result}")
except Exception as e:
    print(f"'zh-TW' failed: {e}")

# Print all supported languages
print("\nSupported languages:")
print(GoogleTranslator().get_supported_languages(as_dict=True))







# (Pdb) p self.slid_model.get_allowed_langs()
# ['kk', 'vi', 'ml', 'ne', 'lb', 'gn', 'mi', 'nl', 'eo', 'ca', 'iw', 'da', 'km', 'ar', 'te', 'mk', 'ko', 'ps', 'mn', 'af', 'gu', 'sa', 'el', 'lv', 'hr', 'no', 'ms', 'haw', 'mg', 'ur', 'sw', 'hu', 'tr', 'jw', 'tg', 'yi', 'hy', 'zh', 'tk', 'gl', 'ha', 'it', 'lt', 'tl', 'nn', 'es', 'ka', 'ceb', 'en', 'am', 'bg', 'si', 'sr', 'id', 'az', 'cs', 'ru', 'pl', 'war', 'mr', 'fo', 'br', 'bn', 'ja', 'et', 'ht', 'my', 'be', 'sk', 'sco', 'sl', 'ta', 'sd', 'kn', 'bs', 'ab', 'gv', 'uk', 'su', 'de', 'sv', 'tt', 'pt', 'ro', 'yo', 'bo', 'fi', 'cy', 'fa', 'pa', 'ba', 'th', 'uz', 'is', 'as', 'lo', 'ln', 'fr', 'oc', 'eu', 'sq', 'hi', 'la', 'so', 'ia', 'mt', 'sn']
# (Pdb) p self.asr_model.allowed_langs
# ['af', 'am', 'ar', 'as', 'az', 'ba', 'be', 'bg', 'bn', 'bo', 'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu', 'fa', 'fi', 'fo', 'fr', 'gl', 'gu', 'ha', 'haw', 'he', 'hi', 'hr', 'ht', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jw', 'ka', 'kk', 'km', 'kn', 'ko', 'la', 'lb', 'ln', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'nn', 'no', 'oc', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'sa', 'sd', 'si', 'sk', 'sl', 'sn', 'so', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tk', 'tl', 'tr', 'tt', 'uk', 'ur', 'uz', 'vi', 'yi', 'yo', 'zh', 'yue']
# (Pdb) self.translater.allowed_langs
# ['af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'be', 'bn', 'bho', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh-CN', 'zh-TW', 'co', 'hr', 'cs', 'da', 'dv', 'doi', 'nl', 'en', 'eo', 'et', 'ee', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'ilo', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'rw', 'gom', 'ko', 'kri', 'ku', 'ckb', 'ky', 'lo', 'la', 'lv', 'ln', 'lt', 'lg', 'lb', 'mk', 'mai', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mni-Mtei', 'lus', 'mn', 'my', 'ne', 'no', 'or', 'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa', 'gd', 'nso', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'ak', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']
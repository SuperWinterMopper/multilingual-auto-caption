from .logger import AppLogger
from ..dataclasses.audio_segment import AudioSegment
import numpy as np
import uuid

class SLIDModel():
    def __init__(self, model, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.model = model
        self.allowed_sample_rates = [16000]  # Silero LID requires 16 kHz audio
        self.index2lang = self.create_silero_index2lang()
        self.logger.logger.info('SLIDModel initialized')
        
    def classify_segments_language(self, audio_segments: list[AudioSegment], allowed_langs: list[str]) -> list[AudioSegment]:
        self.logger.logger.info(f"Beginning language classification for {len(audio_segments)} audio segments")
        
        allowed_langs_set = set(allowed_langs)
        
        for seg in audio_segments:
            try:
                # Validate sample rate
                if seg.sample_rate not in self.allowed_sample_rates:
                    raise ValueError(f"Segment {seg.id} has incorrect sample rate {seg.sample_rate} Hz. Expected one of {self.allowed_sample_rates}")
                
                prediction = self.model.classify_batch(seg.audio)
                
                # Get all predictions sorted by probability
                all_preds = self.parse_all_predictions(prediction)
                
                # Get top k for logging
                top_k_preds = self.get_top_k_predictions(all_preds, k=3)
                
                # Filter to allowed languages and get best match
                filtered_preds = self.filter_predictions_by_allowed_langs(all_preds, allowed_langs_set)
                
                if not filtered_preds:
                    raise ValueError(f"Segment {seg.id}: No predictions match allowed languages {allowed_langs}")
                
                # Assign the highest probability language from allowed_langs
                best_lang = self.get_best_lang(filtered_preds)
                seg.lang = best_lang
                
                # Log predictions with filtering info
                self.log_prediction_results(seg.id, best_lang, top_k_preds, allowed_langs_set)
                    
            except Exception as e:
                self.logger.logger.error(f"Error classifying language for segment {seg.id}: {str(e)}")
                raise
        self.logger.logger.info(f"Completed language classification for {len(audio_segments)} audio segments")
        self.logger.log_audio_segments_list(audio_segments)
        return audio_segments

    def parse_all_predictions(self, prediction) -> dict[str, float]:
        try:
            likelihoods: np.ndarray = np.exp(prediction[0][0].numpy())
            ret = {}
            for i, prob in enumerate(likelihoods):
                lang_code = self.index2lang[i].split(':')[0]
                ret[lang_code] = float(prob)
            return ret
        except Exception as e:
            self.logger.logger.error(f"Error parsing SLID prediction from speechbrain: {str(e)}")
            raise

    def get_top_k_predictions(self, all_preds: dict[str, float], k: int = 3) -> dict[str, float]:
        sorted_preds = sorted(all_preds.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_preds[:k])

    def get_best_lang(self, filtered_preds: dict[str, float]) -> str:
        best_lang, best_prob = "undetermined_lang", float('-inf')
        for lang, prob in filtered_preds.items():
            if prob > best_prob:
                best_lang, best_prob = lang, prob
        return best_lang

    def filter_predictions_by_allowed_langs(self, all_preds: dict[str, float], allowed_langs_set: set[str]) -> dict[str, float]:
        return {lang: prob for lang, prob in all_preds.items() if lang in allowed_langs_set}

    def log_prediction_results(self, seg_id: uuid.UUID, assigned_lang: str, top_k_preds: dict[str, float], allowed_langs_set: set[str]) -> None:
        top_k_langs = set(top_k_preds.keys())
        ignored_langs = top_k_langs - allowed_langs_set
        
        if not ignored_langs:
            # All top k predictions are in allowed_langs
            self.logger.logger.info(f"Segment {seg_id} classified as {assigned_lang} with top predictions: {top_k_preds}")
        else:
            # Some predictions were filtered out
            ignored_preds = {lang: prob for lang, prob in top_k_preds.items() if lang in ignored_langs}
            used_preds = {lang: prob for lang, prob in top_k_preds.items() if lang in allowed_langs_set}
            self.logger.logger.info(
                f"Segment {seg_id} classified as {assigned_lang}. "
                f"Ignored predictions (not in allowed_langs): {ignored_preds}. "
                f"Used predictions: {used_preds}"
            )
    
    @classmethod
    def create_silero_index2lang(cls) -> dict[int, str]:
        return {
            0: 'ab: Abkhazian',
            1: 'af: Afrikaans',
            2: 'am: Amharic',
            3: 'ar: Arabic',
            4: 'as: Assamese',
            5: 'az: Azerbaijani',
            6: 'ba: Bashkir',
            7: 'be: Belarusian',
            8: 'bg: Bulgarian',
            9: 'bn: Bengali',
            10: 'bo: Tibetan',
            11: 'br: Breton',
            12: 'bs: Bosnian',
            13: 'ca: Catalan',
            14: 'ceb: Cebuano',
            15: 'cs: Czech',
            16: 'cy: Welsh',
            17: 'da: Danish',
            18: 'de: German',
            19: 'el: Greek',
            20: 'en: English',
            21: 'eo: Esperanto',
            22: 'es: Spanish',
            23: 'et: Estonian',
            24: 'eu: Basque',
            25: 'fa: Persian',
            26: 'fi: Finnish',
            27: 'fo: Faroese',
            28: 'fr: French',
            29: 'gl: Galician',
            30: 'gn: Guarani',
            31: 'gu: Gujarati',
            32: 'gv: Manx',
            33: 'ha: Hausa',
            34: 'haw: Hawaiian',
            35: 'hi: Hindi',
            36: 'hr: Croatian',
            37: 'ht: Haitian',
            38: 'hu: Hungarian',
            39: 'hy: Armenian',
            40: 'ia: Interlingua',
            41: 'id: Indonesian',
            42: 'is: Icelandic',
            43: 'it: Italian',
            44: 'iw: Hebrew',
            45: 'ja: Japanese',
            46: 'jw: Javanese',
            47: 'ka: Georgian',
            48: 'kk: Kazakh',
            49: 'km: Central Khmer',
            50: 'kn: Kannada',
            51: 'ko: Korean',
            52: 'la: Latin',
            53: 'lb: Luxembourgish',
            54: 'ln: Lingala',
            55: 'lo: Lao',
            56: 'lt: Lithuanian',
            57: 'lv: Latvian',
            58: 'mg: Malagasy',
            59: 'mi: Maori',
            60: 'mk: Macedonian',
            61: 'ml: Malayalam',
            62: 'mn: Mongolian',
            63: 'mr: Marathi',
            64: 'ms: Malay',
            65: 'mt: Maltese',
            66: 'my: Burmese',
            67: 'ne: Nepali',
            68: 'nl: Dutch',
            69: 'nn: Norwegian Nynorsk',
            70: 'no: Norwegian',
            71: 'oc: Occitan',
            72: 'pa: Panjabi',
            73: 'pl: Polish',
            74: 'ps: Pushto',
            75: 'pt: Portuguese',
            76: 'ro: Romanian',
            77: 'ru: Russian',
            78: 'sa: Sanskrit',
            79: 'sco: Scots',
            80: 'sd: Sindhi',
            81: 'si: Sinhala',
            82: 'sk: Slovak',
            83: 'sl: Slovenian',
            84: 'sn: Shona',
            85: 'so: Somali',
            86: 'sq: Albanian',
            87: 'sr: Serbian',
            88: 'su: Sundanese',
            89: 'sv: Swedish',
            90: 'sw: Swahili',
            91: 'ta: Tamil',
            92: 'te: Telugu',
            93: 'tg: Tajik',
            94: 'th: Thai',
            95: 'tk: Turkmen',
            96: 'tl: Tagalog',
            97: 'tr: Turkish',
            98: 'tt: Tatar',
            99: 'uk: Ukrainian',
            100: 'ur: Urdu',
            101: 'uz: Uzbek',
            102: 'vi: Vietnamese',
            103: 'war: Waray',
            104: 'yi: Yiddish',
            105: 'yo: Yoruba',
            106: 'zh: Chinese'
        }
    
    def get_allowed_langs(self) -> list[str]:
        return list(set(lang.split(':')[0] for lang in self.index2lang.values()))
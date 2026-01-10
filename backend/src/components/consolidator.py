from typing import Any


class Consolidator():
    @classmethod
    def consolidate_sample_rates(cls, list_of_sample_rate_lists: list[list[str]]) -> list[str]:
        """Consolidate multiple lists of allowed languages into a single list.

        Args:
            list_of_lang_lists (list[list[str]]): A list containing lists of allowed language codes.

        Returns:
            list[str]: A consolidated list of unique allowed language codes.
        """
        return cls.set_intersection(list_of_sample_rate_lists)
    
    @classmethod
    def consolidate_allowed_langs(cls, langs: list[list[str]]) -> list[str]:
        langs_sets = [set(language_list) for language_list in langs]
        
        normalized_sets = []
        for lang_set in langs_sets:
            normalized = set()
            for lang in lang_set:
                if lang.startswith("zh"):
                    normalized.add("zh")
                else:
                    normalized.add(lang)
            normalized_sets.append(normalized)
        return cls.set_intersection(normalized_sets)
    
    @classmethod
    def set_intersection(cls,lists: list[list[Any]]) -> list[Any]:
        if not lists:
            return []
        
        sets = [set(lst) for lst in lists]
        consolidated = set.intersection(*sets)
        return sorted(list(consolidated))
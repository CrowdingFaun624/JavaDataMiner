from typing import Any

import Comparison.Comparer as Comparer
import Comparison.DataComparer as DataComparer
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import Comparison.DictionaryComparer as DictionaryComparer
import Comparison.SetComparer as SetComparer

class MappingsNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,str], version:str, suppress_domain_errors:bool=False) -> dict[str,str]:
        return data
class NoMappingsNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,str], version:str, suppress_domain_errors:bool=False) -> set[str]:
        return set(data.values())
class ListNormalizer(Normalizer.Normalizer):
    def activate(self, data:list[str], version:str, suppress_domain_errors:bool=False) -> set[str]:
        return set(data)

class SoundEvents(DataComparer.DataComparer):
    set_comparer = SetComparer.SetComparer()
    dict_comparer = DictionaryComparer.DictionaryComparer()

    def get_normalizers(self) -> list[Normalizer.Normalizer]:
        return [
            MappingsNormalizer("19w36a", "-"), # mappings
            NoMappingsNormalizer("1.14_combat-0", "19w35a"), # no mappings
            MappingsNormalizer("1.14.4", "1.14.4"), # mappings
            NoMappingsNormalizer("15w49b", "1.14.4-pre7"), # no mappings
            ListNormalizer("1.8.9", "1.8.9"), # list
            NoMappingsNormalizer("15w43a", "15w49a"), # no mappings
            ListNormalizer("-", "15w42a"), # list
        ]

    def analyze(self, comparison:Any, version1:str, version2:str, total:int) -> str | None:
        if isinstance(comparison, set):
            return self.set_comparer.analyze(comparison, version1, version2, total)
        elif isinstance(comparison, dict):
            return self.dict_comparer.analyze(comparison, version1, version2, total)

    def activate(self, data1:list[str]|dict[str,str], data2:list[str]|dict[str,str], version1:str, version2:str) -> str:
        for item in data1:
            if isinstance(item, D.Difference): raise TypeError(f"Difference object is in data1 between \"{version1}\" and \"{version2}\"!")
        for item in data2:
            if isinstance(item, D.Difference): raise TypeError(f"Difference object is in data2 between \"{version1}\" and \"{version2}\"!")
        normalized_data1 = self.get_normalizer(version1).activate(data1, version1)
        normalized_data2 = self.get_normalizer(version2).activate(data2, version2)
        if isinstance(normalized_data1, set) and isinstance(normalized_data2, dict):
            normalized_data2 = NoMappingsNormalizer.activate(None, normalized_data2, version2)
        elif isinstance(normalized_data1, dict) and isinstance(normalized_data2, set):
            normalized_data1 = NoMappingsNormalizer.activate(None, normalized_data1, version1)
        comparison = self.compare(normalized_data1, normalized_data2)
        return self.analyze(comparison, version1, version2, len(normalized_data2))

import Comparison.Comparer as Comparer
import Comparison.DataComparer as DataComparer
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer

class MappingsNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,str], version:str) -> dict[str,str]:
        return data
class NoMappingsNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,str], version:str) -> set[str]:
        return set(data.values())
class ListNormalizer(Normalizer.Normalizer):
    def activate(self, data:list[str], version:str) -> set[str]:
        return set(data)

class SoundEvents(DataComparer.DataComparer):
    def get_normalizers(self) -> list[Normalizer.Normalizer]:
        return [
            MappingsNormalizer("19w36a", "-"), # mappings
            NoMappingsNormalizer("19w34a", "19w35a"), # no mappings
            MappingsNormalizer("1.14.4", "1.14.4"), # mappings
            NoMappingsNormalizer("15w49b", "1.14.4-pre7"), # no mappings
            ListNormalizer("1.8.9", "1.8.9"), # list
            NoMappingsNormalizer("15w43a", "15w49a"), # no mappings
            ListNormalizer("-", "15w42a"), # list
        ]

    def analyze_set(self, comparison:set[str,D.Difference], version1:str, version2:str, total:int) -> str:
        additions:list[D.Difference] = []
        removals:list[D.Difference] = []
        for item in comparison:
            if isinstance(item, D.Difference):
                if item.is_addition(): additions.append(item)
                elif item.is_change(): raise ValueError(f"Difference of type \"Change\" found in SoundEvents Comparison between \"{version1}\" and \"{version2}\"!")
                elif item.is_removal(): removals.append(item)
        additions.sort()
        removals.sort()
        if len(additions) == 0 and len(removals) == 0: return None
        output = f"{version2} (from {version1})\n\nTotal: {total} (+{len(additions)}, -{len(removals)})\n\n"
        if len(additions) > 0:
            output += "Additions:\n"
            for addition in additions:
                output += f"\tAdded {addition.new}\n"
            output += "\n"
        if len(removals) > 0:
            output += "Removals:\n"
            for removal in removals:
                output += f"\tRemoved {removal.old}\n"
            output += "\n"
        return output

    def analyze_dict(self, comparison:dict[str,str|D.Difference], version1:str, version2:str, total:int) -> str:
        additions:dict[str,D.Difference] = {}
        changes:dict[str,D.Difference] = {}
        removals:dict[str,D.Difference] = {}
        for name, item in list(comparison.items()):
            if isinstance(item, D.Difference):
                if item.is_addition(): additions[name] = item
                elif item.is_change(): changes[name] = item
                elif item.is_removal(): removals[name] = item
        additions = self.sort_dict(additions)
        changes = self.sort_dict(changes)
        removals = self.sort_dict(removals)
        if len(additions) == 0 and len(changes) == 0 and len(removals) == 0: return None
        output = f"{version2} (from {version1})\n\n)\n\nTotal: {total} (+{len(additions)}, -{len(removals)})\n\n"
        if len(additions) > 0:
            output += "Additions:\n"
            for name, addition in list(additions.items()):
                output += f"\tAdded {name}: {addition.new}\n"
            output += "\n"
        if len(changes) > 0:
            output += "Changes:\n"
            for name, change in list(changes.items()):
                output += f"\tChanged {name} from {change.old} to {change.new}\n"
            output += "\n"
        if len(removals) > 0:
            output += "Removals:\n"
            for name, removal in list(removals.items()):
                output += f"\tRemoved {name}: {removal.old}\n"
            output += "\n"
        return output

    def activate(self, data1:list[str]|dict[str,str], data2:list[str]|dict[str,str], version1:str, version2:str) -> str:
        for item in data1:
            if isinstance(item, D.Difference): raise TypeError(f"Difference object is in data1 between \"{version1}\" and \"{version2}\"!")
        for item in data2:
            if isinstance(item, D.Difference): raise TypeError(f"Difference object is in data2 between \"{version1}\" and \"{version2}\"!")
        normalized_data1 = self.get_normalizer(version1).activate(data1, version1)
        normalized_data2 = self.get_normalizer(version2).activate(data2, version2)
        if isinstance(normalized_data1, set) and isinstance(normalized_data2, dict):
            normalized_data2 = set(normalized_data2.values())
        elif isinstance(normalized_data1, dict) and isinstance(normalized_data2, set):
            normalized_data1 = set(normalized_data1.values())
        comparison = self.compare(normalized_data1, normalized_data2)
        if isinstance(normalized_data1, set):
            return self.analyze_set(comparison, version1, version2, len(normalized_data2))
        elif isinstance(normalized_data1, dict):
            return self.analyze_dict(comparison, version1, version2, len(normalized_data2))

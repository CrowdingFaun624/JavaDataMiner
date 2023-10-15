import json
from typing import Any

import Comparison.Comparer as Comparer
import Comparison.DataComparer as DataComparer
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer

class NoMappingsNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,dict[str,str|float]], version:str, suppress_domain_errors:bool=False) -> list[dict[str,str|float]]:
        for name in data.keys():
            if not suppress_domain_errors and len(name) > 2: raise ValueError("Sound type name \"%s\" looks like it is mapped in %s!" % (name, version))
        return list(data.values())
class MappingsNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,dict[str,str|float]], version:str, suppress_domain_errors:bool=False) -> dict[str,dict[str,str|float]]:
        for name in data.keys():
            if not suppress_domain_errors and len(name) <= 2: raise ValueError("Sound type name \"%s\" looks like it is unmapped in %s!" % (name, version))
        return data

class SoundTypeComparer(DataComparer.DataComparer):
    def __init__(self, add_message="\tAdded %s\n", change_message="\t%s:\n", remove_message="\t\tRemoved %s\n", property_add_message="\t\tAdded %s as %s\n", property_change_message="\t\tChanged %s from %s to %s\n", property_remove_message="\t\tRemoved %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
        self.property_add_message = property_add_message
        self.property_change_message = property_change_message
        self.property_remove_message = property_remove_message
    
    def get_normalizers(self) -> list[Normalizer.Normalizer]:
        return [
            MappingsNormalizer("19w36a", "-"),
            NoMappingsNormalizer("1.14_combat-0", "19w35a"),
            MappingsNormalizer("1.14.4", "1.14.4"),
            NoMappingsNormalizer("-", "1.14.4-pre7"),
        ]

    def get_properties_string(self, properties:dict[str,str|float]) -> str:
        return "".join("\t\t%s: %s\n" % (key, value) for key, value in properties.items())

    def analyze_set(self, comparison:list[dict[str,str|float|D.Difference]|D.Difference], version1:str, version2:str, total:int) -> str|None:
        additions:list[D.Difference] = []
        removals:list[D.Difference] = []
        for properties in comparison:
            if isinstance(properties, D.Difference):
                if properties.is_addition(): additions.append(properties)
                elif properties.is_change(): raise ValueError("Difference of type \"Change\" found in Blocks Comparison between \"%s\" and \"%s\"!" % (version1, version2))
                elif properties.is_removal(): removals.append(properties)
        if len(additions) == 0 and len(removals) == 0: return None
        output = f"{version2} (from {version1})\n\nTotal: {total} (+{len(additions)}, -{len(removals)})\n\n"
        if len(additions) > 0:
            output += "Additions:\n"
            for properties in additions:
                output += self.change_message % "Added"
                output += self.get_properties_string(properties.new)
            output += "\n"
        if len(removals) > 0:
            output += "Removals:\n"
            for properties in removals:
                output += self.change_message % "Removed"
                output += self.get_properties_string(properties.old)
            output += "\n"
        return output

    def analyze_dict(self, comparison:dict[str,dict[str,str|float|D.Difference]|D.Difference], version1:str, version2:str, total:int) -> str|None:
        additions:list[tuple[str,D.Difference]] = [] # names, property values
        changes:list[tuple[str,str,D.Difference]] = [] # names, property names, property values
        removals:list[str] = [] # names
        for name, properties in list(comparison.items()):
            if isinstance(properties, D.Difference):
                if properties.is_addition(): additions.append((name, properties))
                elif properties.is_change(): raise ValueError("Difference of type \"Change\" found in Blocks Comparison between \"%s\" and \"%s\"!" % (version1, version2))
                elif properties.is_removal(): removals.append(name)
            elif isinstance(properties, dict):
                for property_name, property_value in properties.items():
                    if isinstance(property_value, D.Difference):
                        changes.append((name, property_name, property_value))
        additions.sort()
        changes.sort()
        removals.sort()
        if len(additions) == 0 and len(removals) == 0 and len(changes) == 0: return None
        output = f"{version2} (from {version1})\n\nTotal: {total} (+{len(additions)}, -{len(removals)})\n\n"
        if len(additions) > 0:
            output += "Additions:\n"
            for name, properties in additions:
                output += self.add_message % json.dumps(name)
                output += self.get_properties_string(properties.new)
            output += "\n"
        if len(removals) > 0:
            output += "Removals:\n"
            for name in removals:
                output += self.remove_message % json.dumps(name)
            output += "\n"
        if len(changes) > 0:
            output += "Changes:\n"
            current_block = None
            for name, property_name, property_value in changes:
                if current_block != name:
                    current_block = name
                    output += self.change_message % name
                if property_value.is_addition(): output += self.property_add_message % (property_name, property_value.new)
                elif property_value.is_change(): output += self.property_change_message % (property_name, property_value.old, property_value.new)
                elif property_value.is_removal(): output += self.property_remove_message % property_name
            output += "\n"
        return output

    def analyze(self, comparison:Any, version1:str, version2:str, total:int) -> str|None:
        if isinstance(comparison, list):
            return self.analyze_set(comparison, version1, version2, total)
        elif isinstance(comparison, dict):
            return self.analyze_dict(comparison, version1, version2, total)
        else: raise TypeError("Invalid type \"%s\" of comparison between \"%s\" and \"%s\"!" % (str(type(comparison)), version1, version2))

    def activate(self, data1:dict[str,dict[str,int|str]], data2:dict[str,dict[str,int|str]], version1:str, version2:str) -> str:
        normalized_data1 = self.get_normalizer(version1).activate(data1, version1)
        normalized_data2 = self.get_normalizer(version2).activate(data2, version2)
        if isinstance(normalized_data1, list) and isinstance(normalized_data2, dict):
            normalized_data2 = NoMappingsNormalizer.activate(None, normalized_data2, version2, suppress_domain_errors=True)
        elif isinstance(normalized_data1, dict) and isinstance(normalized_data2, list):
            normalized_data1 = NoMappingsNormalizer.activate(None, normalized_data1, version1, suppress_domain_errors=True)
        type_hint = {list: set, dict:dict}[type(normalized_data1)]
        comparison:dict[str,dict[str,int|str]] = Comparer.compare(normalized_data1, normalized_data2, type_hint=type_hint)
        return self.analyze(comparison, version1, version2, len(data2))

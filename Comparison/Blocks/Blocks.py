from typing import Any

import Comparison.Comparer as Comparer
import Comparison.DataComparer as DataComparer
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import DataMiners.SoundType.SoundType as SoundType

class BlocksNormalizer5(Normalizer.Normalizer):
    def shorten_sound_type(self, sound_type:dict[str,str|float]) -> str:
        return ",".join(str(value) for value in sound_type.values())
    def activate(self, data:dict[str,dict[str,Any]], version:str, suppress_domain_errors:bool=False) -> dict[str,dict[str,Any]]:
        sound_type_file = SoundType.SoundType.get_data_file(version)
        new_data:dict[str,dict[str,Any]] = {}
        for block_id, block_data in list(data.items()):
            if block_data["sound_type"] not in sound_type_file: print(data); raise KeyError("Block \"%s\"'s sound type \"%s\" does not exist in the sound type file in %s!" % (str(block_id), block_data["sound_type"], version))
            if not suppress_domain_errors and not block_id.isdigit(): raise ValueError("\"%s\" is an alpha string instead of a numeric ID in %s!" % (block_id, version))
            block_sound_type = self.shorten_sound_type(sound_type_file[block_data["sound_type"]])
            new_data[block_id] = {"sound_type": block_sound_type} # forget code name; it is useless anyways.
        return new_data

class BlocksNormalizer4(Normalizer.Normalizer):
    def shorten_sound_type(self, sound_type:dict[str,str|float]) -> str:
        return ",".join(str(value) for value in sound_type.values())
    def activate(self, data:dict[str,dict[str,Any]], version:str, suppress_domain_errors:bool=False) -> dict[str,dict[str,Any]]:
        sound_type_file = SoundType.SoundType.get_data_file(version)
        new_data:dict[str,dict[str,Any]] = {}
        for block_code_name, block_data in list(data.items()):
            if "name" not in block_data: raise KeyError("\"name\" is not a property in block \"%s\" with properties \"%s\" in %s!" % (block_code_name, str(block_data), version))
            if "id" not in block_data: raise KeyError("\"id\" is not a property in block \"%s\" with properties \"%s\" in %s!" % (block_code_name, str(block_data), version))
            if block_data["name"] is None: block_id = str(block_data["id"]) # fallback because name can be null.
            else: block_id = str(block_data["id"]) + ":" + block_data["name"]
            if block_data["sound_type"] not in sound_type_file: print(data); raise KeyError("Block \"%s\"'s sound type \"%s\" does not exist in the sound type file in %s!" % (str(block_id), block_data["sound_type"], version))
            block_sound_type = self.shorten_sound_type(sound_type_file[block_data["sound_type"]])
            new_data[block_id] = {"sound_type": block_sound_type} # forget code name; it is useless anyways.
        return new_data

class BlocksNormalizer3(Normalizer.Normalizer):
    def shorten_sound_type(self, sound_type:dict[str,str|float]) -> str:
        return ",".join(str(value) for value in sound_type.values())
    def activate(self, data:dict[str,dict[str,Any]], version:str, suppress_domain_errors:bool=False) -> dict[str,dict[str,Any]]:
        sound_type_file = SoundType.SoundType.get_data_file(version)
        new_data:dict[str,dict[str,Any]] = {}
        for block_code_name, block_data in list(data.items()):
            if "new_name" not in block_data: raise KeyError("\"new_name\" is not a property in block \"%s\" with properties \"%s\" in %s!" % (block_code_name, str(block_data), version))
            if "old_name" not in block_data: raise KeyError("\"old_name\" is not a property in block \"%s\" with properties \"%s\" in %s!" % (block_code_name, str(block_data), version))
            if "id" not in block_data: raise KeyError("\"id\" is not a property in block \"%s\" with properties \"%s\" in %s!" % (block_code_name, str(block_data), version))
            if block_data["new_name"] is not None: block_id = str(block_data["id"]) + ":" + block_data["new_name"]
            elif block_data["old_name"] is not None: block_id = str(block_data["id"]) + ":" + block_data["old_name"]
            else: block_id = str(block_data["id"])
            if block_data["sound_type"] not in sound_type_file: print(data); raise KeyError("Block \"%s\"'s sound type \"%s\" does not exist in the sound type file in %s!" % (str(block_id), block_data["sound_type"], version))
            block_sound_type = self.shorten_sound_type(sound_type_file[block_data["sound_type"]])
            new_data[block_id] = {"sound_type": block_sound_type} # forget code name; it is useless anyways.
        return new_data
# I think that I might have been completely insane when I built those blocks dataminers.
class BlocksNormalizer2(Normalizer.Normalizer):
    def shorten_sound_type(self, sound_type:dict[str,str|float]) -> str:
        return ",".join(str(value) for value in sound_type.values())
    def activate(self, data:dict[str,dict[str,Any]], version:str, suppress_domain_errors:bool=False) -> dict[str,dict[str,Any]]:
        sound_type_file = SoundType.SoundType.get_data_file(version)
        new_data:dict[str,dict[str,Any]] = {}
        for block_id, block_data in list(data.items()):
            if block_data["sound_type"] not in sound_type_file: print(data); raise KeyError("Block \"%s\"'s sound type \"%s\" does not exist in the sound type file in %s!" % (str(block_id), block_data["sound_type"], version))
            block_sound_type = self.shorten_sound_type(sound_type_file[block_data["sound_type"]])
            new_data[block_id] = {"sound_type": block_sound_type} # forget code name; it is useless anyways.
        return new_data

class BlocksNormalizer1(Normalizer.Normalizer):
    def activate(self, data:dict[str,dict[str,Any]], version:str, suppress_domain_errors:bool=False) -> dict[str,dict[str,Any]]:
        new_data:dict[str,dict[str,Any]] = {}
        for block_id, block_data in list(data.items()):
            if not suppress_domain_errors and "sound_type_code_name" not in block_data or "code_name" not in block_data: print(data); raise ValueError("`NamedSoundTypesNormalizer is being used on the wrong version %s!" % version)
            new_data[block_id] = {"sound_type": block_data["sound_type"]}
        return new_data

class BlocksNormalizer0(Normalizer.Normalizer):
    def activate(self, data:dict[str,dict[str,Any]], version:str, suppress_domain_errors:bool=False) -> dict[str,dict[str,Any]]:
        new_data:dict[str,dict[str,Any]] = {}
        for block_id, block_data in list(data.items()):
            if not suppress_domain_errors and len(block_data) != 1 or "sound_type" not in block_data:
                raise ValueError("Invalid data in %s at block \"%s\"!" % (version, str(block_id)))
            if isinstance(block_data["sound_type"], str):
                new_data[block_id] = {"sound_type": block_data["sound_type"]}
            elif isinstance(block_data["sound_type"], list):
                new_data[block_id] = {"sound_type": str(block_data["sound_type"])}
            else: raise TypeError("Invalid type of sound type \"%s\" in block \"%s\" in %s!" % (str(block_data["sound_type"]), block_id, version))
        return new_data

class BlocksComparer(DataComparer.DataComparer):
    def __init__(self, add_message="\tAdded %s\n", change_message="\tChanged %s's \"%s\" from %s to %s\n", remove_message="\tRemoved %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
    
    def get_normalizers(self) -> Normalizer.Normalizer:
        return [
            BlocksNormalizer0("19w36a", "-"),
            BlocksNormalizer1("1.14_combat-0", "19w35a"),
            BlocksNormalizer0("1.14.4", "1.14.4"),
            BlocksNormalizer1("15w43a", "1.14.4-pre7"),
            BlocksNormalizer2("13w36a", "15w42a"),
            BlocksNormalizer3("13w24a", "1.6.4"),
            BlocksNormalizer4("b1.0", "13w23b"),
            BlocksNormalizer5("-", "a1.2.6"),
        ]
    
    def analyze(self, comparison:dict[str|int,dict[str,Any|D.Difference]|D.Difference], version1:str, version2:str, total:int) -> str|None:
        additions:list[str] = [] # list of block ids that changed
        changes:list[tuple[str,str]] = [] # list of (block id, property name) that changed
        removals:list[str] = [] # list of block ids that changed
        for block_id, block_properties in list(comparison.items()):
            if isinstance(block_properties, D.Difference):
                if block_properties.is_addition(): additions.append(block_id)
                elif block_properties.is_change(): raise ValueError("Difference of type \"Change\" found in Blocks Comparison between \"%s\" and \"%s\"!" % (version1, version2))
                elif block_properties.is_removal(): removals.append(block_id)
            elif D.Difference in (type(property) for property in block_properties.values()):
                for property_name, property_value in list(block_properties.items()):
                    if property_value.is_addition(): raise ValueError("Difference of type \"Addition\" found in Blocks Comparison of block \"%s\" between \"%s\" and \"%s\"!" % (str(block_id), version1, version2))
                    if property_value.is_change(): changes.append((block_id, property_name))
                    if property_value.is_removal(): raise ValueError("Difference of type \"Removal\" found in Blocks Comparison of block \"%s\" between \"%s\" and \"%s\"!" % (str(block_id), version1, version2))
        additions.sort()
        changes.sort()
        removals.sort()
        if len(additions) == 0 and len(changes) == 0 and len(removals) == 0: return None
        output = f"{version2} (from {version1})\n\nTotal: {total} (+{len(additions)}, -{len(removals)})\n\n"
        if len(additions) > 0:
            output += "Additions:\n"
            for addition in additions:
                output += self.add_message % addition
            output += "\n"
        if len(removals) > 0:
            output += "Removals:\n"
            for removal in removals:
                output += self.remove_message % removal
            output += "\n"
        if len(changes) > 0:
            output += "Changes:\n"
            for change_block, change_property in changes:
                difference = comparison[change_block][change_property]
                output += self.change_message % (change_block, change_property, difference.old, difference.new)
            output += "\n"
        return output

    def activate(self, data1:dict[str,dict[str,any]], data2:dict[str,dict[str,any]], version1:str, version2:str) -> str:
        for item in data1:
            if isinstance(item, D.Difference): raise TypeError(f"Difference object is in data1 between \"{version1}\" and \"{version2}\"!")
        for item in data2:
            if isinstance(item, D.Difference): raise TypeError(f"Difference object is in data2 between \"{version1}\" and \"{version2}\"!")
        normalized_data1:dict[str,dict[str,Any]] = self.get_normalizer(version1).activate(data1, version1)
        normalized_data2:dict[str,dict[str,Any]] = self.get_normalizer(version2).activate(data2, version2)
        if len(normalized_data1) != 0 and len(normalized_data2) != 0 and type(list(normalized_data1.keys())[0]) != type(list(normalized_data2.keys())[0]): return None # formats are completely different; just skip.
        comparison:dict[str,dict[str,Any]] = Comparer.compare(normalized_data1, normalized_data2)
        return self.analyze(comparison, version1, version2, len(normalized_data2))

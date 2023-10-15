from typing import Any, Callable

import Comparison.DataComparer as DataComparer
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import DataMiners.Blocks.Blocks as Blocks
import DataMiners.SoundType.SoundType as SoundType

def cast(data:list|D.Difference, cast_type:type|Callable):
    '''Turns the data into the `cast_type`, whether it is a difference or not.'''
    if isinstance(data, D.Difference): return data.cast(cast_type)
    else: return cast_type(data)

def stringify_sound_type(sound_type:dict[str,str|int], already:set[str]|None=None) -> str:
    def get_block(sound_event:str) -> str:
        if sound_event.startswith("step.") or sound_event.startswith("dig."): return sound_event.split(".")[1]
        elif sound_event.startswith("block."): return sound_event.split(".")[1]
        else: return sound_event
    output = str(sound_type["volume"]) +";" + str(sound_type["pitch"]) + ";"
    possible_keys = ["dig", "step", "dig2", "break", "step", "place", "hit", "fall"]
    sound_events:list[str] = []
    for key in possible_keys:
        if key in sound_type: sound_events.append(get_block(sound_type[key]))
    if len(set(sound_events)) == 1: output += sound_events[0]
    else: output += ";".join(sound_events)
    if already is not None:
        new_output = output
        index = 1
        while new_output in already: # prepends the lowest possible number to the beginning of the string if it already exists.
            new_output = str(index) + ";" + output
            index += 1
        output = new_output
    return output

class NumericBlockNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,list[str]], version:str, suppress_domain_errors:bool=False) -> dict[str,set[int]]:
        sound_type_data = SoundType.SoundType.get_data_file(version)
        output:dict[str,set[str]] = {}
        sound_type_names:set[str] = set()
        for type_name, type_content in list(data.items()):
            new_type_content = []
            for block_name in type_content:
                if not suppress_domain_errors and (not isinstance(block_name, str) or not block_name.isnumeric()): raise ValueError("\"%s\" is not a string-numeric id in %s!" % (str(block_name), version))
                new_type_content.append(cast(block_name, int))
            if not suppress_domain_errors and len(type_name) > 2: raise ValueError("\"%s\" is not a valid code name for a sound type in %s!" % (type_name, version))
            if type_name not in sound_type_data: raise KeyError("Sound type \"%s\" not found in %s!" % (type_name, version))
            new_type_name = stringify_sound_type(sound_type_data[type_name], sound_type_names)
            sound_type_names.add(new_type_name)
            if new_type_name in output: raise KeyError("Sound type \"%s\" already exists in %s!" % (new_type_name, version))
            output[new_type_name] = cast(new_type_content, set)
        return output

class LetterBlockNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,list[str]], version:str, suppress_domain_errors:bool=False) -> dict[str,set[str]]:
        output:dict[str,set[str]] = {}
        blocks_data:dict[str,dict[str,Any]] = Blocks.Blocks.get_data_file(version)
        sound_type_data = SoundType.SoundType.get_data_file(version)
        sound_type_names:set[str] = set()
        for type_name, type_content in list(data.items()):
            new_type_content = []
            for block_code_name in type_content:
                if not suppress_domain_errors and (not isinstance(block_code_name, str) or len(block_code_name) > 2 or not block_code_name.isalpha()): raise ValueError("\"%s\" is not a valid code name in %s!" % (str(block_code_name), version))
                if block_code_name not in blocks_data: raise KeyError("Block code name \"%s\" was not found in %s!" % (block_code_name, version))
                if "name" not in blocks_data[block_code_name]: raise KeyError("Block \"name\" attribute not found for %s in %s!" % (block_code_name, version))
                if "id" not in blocks_data[block_code_name]: raise KeyError("Block \"id\" attribute not found for %s in %s!" % (block_code_name, version))
                if blocks_data[block_code_name]["name"] is not None: block_id = blocks_data[block_code_name]["name"]
                else: block_id = cast(blocks_data[block_code_name]["id"], str)
                if "minecraft:" in block_id: raise ValueError("Namespace in block id \"%s\" in %s!" % (block_id, version))
                new_type_content.append(block_id)
            if not suppress_domain_errors and len(type_name) > 2: raise ValueError("\"%s\" is not a valid code name for a sound type in %s!" % (type_name, version))
            if type_name not in sound_type_data: raise KeyError("Sound type \"%s\" not found in %s!" % (type_name, version))
            new_type_name = stringify_sound_type(sound_type_data[type_name], sound_type_names)
            sound_type_names.add(new_type_name)
            if new_type_name in output: raise KeyError("Sound type \"%s\" already exists in %s!" % (new_type_name, version))
            output[new_type_name] = cast(new_type_content, set)
        return output

class SplitNameBlockNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,list[str]], version:str, suppress_domain_errors:bool=False) -> dict[str,set[str]]:
        output:dict[str,set[str]] = {}
        blocks_data:dict[str,dict[str,Any]] = Blocks.Blocks.get_data_file(version)
        sound_type_data = SoundType.SoundType.get_data_file(version)
        sound_type_names:set[str] = set()
        for type_name, type_content in list(data.items()):
            new_type_content = []
            for block_code_name in type_content:
                if not suppress_domain_errors and (not isinstance(block_code_name, str) or len(block_code_name) > 2 or not block_code_name.isalpha()): raise ValueError("\"%s\" is not a valid code name in %s!" % (str(block_code_name), version))
                if block_code_name not in blocks_data: raise KeyError("Block code name \"%s\" was not found in %s!" % (block_code_name, version))
                if "new_name" not in blocks_data[block_code_name]: raise KeyError("Block \"new_name\" attribute not found for %s in %s!" % (block_code_name, version))
                if "old_name" not in blocks_data[block_code_name]: raise KeyError("Block \"old_name\" attribute not found for %s in %s!" % (block_code_name, version))
                if "id" not in blocks_data[block_code_name]: raise KeyError("Block \"id\" attribute not found for %s in %s!" % (block_code_name, version))
                if blocks_data[block_code_name]["new_name"] is not None: block_id = blocks_data[block_code_name]["new_name"]
                if blocks_data[block_code_name]["old_name"] is not None: block_id = blocks_data[block_code_name]["old_name"]
                else: block_id = cast(blocks_data[block_code_name]["id"], str)
                if "minecraft:" in block_id: raise ValueError("Namespace in block id \"%s\" in %s!" % (block_id, version))
                new_type_content.append(block_id)
            if not suppress_domain_errors and len(type_name) > 2: raise ValueError("\"%s\" is not a valid code name for a sound type in %s!" % (type_name, version))
            if type_name not in sound_type_data: raise KeyError("Sound type \"%s\" not found in %s!" % (type_name, version))
            new_type_name = stringify_sound_type(sound_type_data[type_name], sound_type_names)
            sound_type_names.add(new_type_name)
            if new_type_name in output: raise KeyError("Sound type \"%s\" already exists in %s!" % (new_type_name, version))
            output[new_type_name] = cast(new_type_content, set)
        return output

class NiceNameBlockNormalizer(Normalizer.Normalizer):
    def remove_namespace(self, block_name:str) -> str:
        if block_name.startswith("minecraft:"):
            block_name = block_name.replace("minecraft:", "", 1)
        return block_name
    def activate(self, data:dict[str,list[str]], version:str, suppress_domain_errors:bool=False) -> dict[str,set[str]]:
        output:dict[str,set[str]] = {}
        sound_type_data = SoundType.SoundType.get_data_file(version)
        sound_type_names:set[str] = set()
        for type_name, type_content in list(data.items()):
            new_type_content = []
            for block_name in type_content:
                if not suppress_domain_errors and (not isinstance(block_name, str) or len(block_name) <= 2): raise ValueError("\"%s\" is not a valid id in %s!" % (str(block_name), version))
                new_type_content.append(cast(block_name, self.remove_namespace))
            if not suppress_domain_errors and len(type_name) > 2: raise ValueError("\"%s\" is not a valid code name for a sound type in %s!" % (type_name, version))
            if type_name not in sound_type_data: raise KeyError("Sound type \"%s\" not found in %s!" % (type_name, version))
            new_type_name = stringify_sound_type(sound_type_data[type_name], sound_type_names)
            sound_type_names.add(new_type_name)
            if new_type_name in output: raise KeyError("Sound type \"%s\" already exists in %s!" % (new_type_name, version))
            output[new_type_name] = cast(new_type_content, set)
        return output

class MappingsBlockNormalizer(Normalizer.Normalizer):
    def activate(self, data:dict[str,list[str]], version:str, suppress_domain_errors:bool=False) -> dict[str,set[str]]:
        output:dict[str,set[str]] = {}
        for type_name, type_content in list(data.items()):
            new_type_content = []
            for block_name in type_content:
                if not suppress_domain_errors and (not isinstance(block_name, str) or len(block_name) <= 2): raise ValueError("\"%s\" is not a valid id in %s!" % (str(block_name), version))
                new_type_content.append(block_name)
            if not suppress_domain_errors and len(type_name) <= 2: raise ValueError("\"%s\" is not a valid sound type name in %s!" % (type_name, version))
            output[type_name] = cast(new_type_content, set)
        return output


class SoundTypeBlocksComparer(DataComparer.DataComparer):
    def __init__(self, add_message="\tAdded %s to %s\n", change_message="CHANGE ERROR\n", remove_message="\tRemoved %s from %s\n", add_type_message="\tAdded type %s with blocks:\n%s\n", remove_type_message="\tRemoved type %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
        self.add_type_message = add_type_message
        self.remove_type_message = remove_type_message
    
    def get_normalizers(self) -> list[Normalizer.Normalizer]:
        return [
            MappingsBlockNormalizer("19w36a", "-"),
            NiceNameBlockNormalizer("1.14_combat-0", "19w35a"),
            MappingsBlockNormalizer("1.14.4", "1.14.4"),
            NiceNameBlockNormalizer("13w36a", "1.14.4-pre7"),
            SplitNameBlockNormalizer("13w24a", "1.6.4"),
            LetterBlockNormalizer("b1.0", "13w23b"),
            NumericBlockNormalizer("-", "a1.2.6"),
        ]
    
    def analyze(self, comparison:dict[str,set[str]], version1:str, version2:str, total:int) -> str|None:
        type_additions:list[tuple[str,list[str]]] = []
        type_removals:list[str] = []
        additions:list[tuple[str,str]] = []
        removals:list[tuple[str,str]] = []
        for type_name, type_content in list(comparison.items()):
            if isinstance(type_content, D.Difference):
                if type_content.is_addition(): type_additions.append((type_name, sorted(list(type_content.new))))
                elif type_content.is_change(): raise ValueError("Difference cannot be type change!")
                elif type_content.is_removal(): type_removals.append(type_name)
            else:
                for block_name in type_content:
                    if isinstance(block_name, D.Difference):
                        if block_name.is_addition(): additions.append((type_name, block_name.new))
                        elif block_name.is_change(): raise ValueError("Block name cannot be type change!")
                        elif block_name.is_removal(): removals.append((type_name, block_name.old))
        type_additions.sort()
        type_removals.sort()
        additions.sort()
        removals.sort()
        if len(type_additions) == 0 and len(type_removals) == 0 and len(additions) == 0 and len(removals) == 0: return None
        output = f"{version2} (from {version1})\n\nTotal: {total} (+{len(additions)}, -{len(removals)})\n\n"
        if len(type_additions) > 0:
            output += "Type Additions:\n"
            for type_name, type_contents in type_additions:
                output += self.add_type_message % (type_name, "\n".join("\t\t" + str(item) for item in type_contents))
            output += "\n"
        if len(type_removals) > 0:
            output += "Type Removals:\n"
            for type_name in type_removals:
                output += self.remove_type_message % type_name
            output += "\n"
        if len(additions) > 0:
            output += "Additions:\n"
            for type_name, block_name in additions:
                output += self.add_message % (block_name, type_name)
            output += "\n"
        if len(removals) > 0:
            output += "Removals:\n"
            for type_name, block_name in removals:
                output += self.remove_message % (block_name, type_name)
            output += "\n"
        return output
        
    def activate(self, data1:dict[str,list[str]], data2:dict[str,list[str]], version1:str, version2:str) -> str|None:
        normalizer1 = self.get_normalizer(version1)
        normalizer2 = self.get_normalizer(version2)
        normalized_data1:dict[str,set[str]] = normalizer1.activate(data1, version1)
        normalized_data2:dict[str,set[str]] = normalizer2.activate(data2, version2)
        if type(normalizer1) != type(normalizer2): return None
        comparison:dict[str,set[str]] = self.compare(normalized_data1, normalized_data2)
        return self.analyze(comparison, version1, version2, len(normalized_data2))

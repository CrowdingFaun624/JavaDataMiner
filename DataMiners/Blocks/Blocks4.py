import os

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks4(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.blocks_list_record_threshold = 1
        self.sound_type_overrides = {"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "acacia_stairs": "wood", "dark_oak_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone", "red_sandstone_stairs": "stone"}
        if "blocks_list_record_threshold" in kwargs:
            self.blocks_list_record_threshold = kwargs["blocks_list_record_threshold"]
        if "sound_type_overrides" in kwargs:
            self.sound_type_overrides = kwargs["sound_type_overrides"]
    
    def search(self, version:str) -> str:
        '''Returns the file path of Blocks.java (e.g. art.java)'''
        blocks_files = Searcher.search(version, "client", ["stone", "grass", "leaves", "dispenser", "not:name_tag", "not:Bootstrap"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def search_blocks_list(self, version:str) -> str:
        '''Returns the file path of BlocksList.java (e.g. aru.java)'''
        blocks_files = Searcher.search(version, "client", ["stone", "grass", "leaves", "dispenser", "not:name_tag", "Bootstrap"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many BlocksList files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No BlocksList file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def analyze_block_list(self, file_contents:list[str], version:str) -> tuple[dict[str,str], dict[str,str], str]:
        '''Returns a dict of `{game name: code_name}`, `{game name: file name}`, and the default block type.'''
        def should_continue(line:str) -> bool:
            for continue_thing in CONTINUES:
                if continue_thing in line: return True
            else: return False
        RECORD_START = "        }"
        RECORD_END = "    }"
        DEFAULT_FILE_DECLARATION = "    private static "
        CONTINUES = ["ashSet", ".clear();"]
        recording = False
        start_threshold = 0
        names:dict[str,str] = {}
        files:dict[str,str] = {}
        for line in file_contents:
            line = line.rstrip()
            if should_continue(line): continue
            elif line.startswith(DEFAULT_FILE_DECLARATION):
                default_file = line.replace(DEFAULT_FILE_DECLARATION, "").split(" ")[0]
            elif line.startswith(RECORD_START):
                if recording:
                    raise ValueError("Recording line encountered multiple times in Blocks in %s!" % version)
                start_threshold += 1
                if start_threshold >= self.blocks_list_record_threshold: recording = True
            elif line.startswith(RECORD_END) and recording: recording = False; break
            elif recording:
                if "\"" not in line: raise ValueError("Line \"%s\" in BlocksList in %s is wonky!" % (line.lstrip(), version))
                split_line = line.lstrip().split(" ")
                code_name = split_line[0]
                game_name = line.split("\"")[-2]
                has_different_file = split_line[2].startswith("(")
                if has_different_file:
                    file = split_line[2].split(")")[0][1:]
                else: file = default_file
                names[game_name] = code_name
                files[game_name] = file
        else: # if code did not break before end of file
            raise ValueError("BlocksList in %s did not break before end of file!" % version)
        return names, files, default_file

    def find_soundtype(self, line:str, sound_types:dict[str,dict[str,int|str]], default_sound_type:str, key:str=".a(%s)") -> str|None:
        '''Returns a soundtype from a line, e.g. "i", "g" or "b".'''
        for sound_type in list(sound_types.keys()):
            sound_type_text = key % sound_type # "a" is not a variable because there should only be one function with an input of a soundtype
            if sound_type_text in line: return sound_type
        else: return default_sound_type

    def find_other_class_name(self, line:str) -> str:
        '''Extracts an extended class from a string (e.g. "new aic()..." -> aic)'''
        NEW_DECLARER = "new "
        if NEW_DECLARER not in line: return None
        return line.split(NEW_DECLARER)[1].split("(")[0].split(".")[0]

    def remove_nones(self, input_dict:dict) -> dict:
        output = {}
        for key, value in list(input_dict.items()):
            if value is not None:
                output[key] = value
        return output

    def evaluate_template(self, line:str, version:str, sound_types:dict[str,dict[str,int|str]], default_sound_type:str) -> tuple[str,dict[str,any]]:
        split_line = line.lstrip().split(" ")
        if split_line[1] == "=":
            template_name = split_line[0]
        elif split_line[2] == "=":
            template_name = split_line[1]
        else: raise ValueError("\"=\" in Blocks in %s is in a weird position in line \"%s\"" % (version, line))
        sound_type = self.find_soundtype(line, sound_types, None)
        class_extension = self.find_other_class_name(line)
        return template_name, self.remove_nones({"sound_type": sound_type, "class_extension": class_extension})

    def evaluate_block(self, line:str, version:str, templates:dict[str,dict[str,any]], sound_types:dict[str,dict[str,int|str]], default_sound_type:str) -> tuple[str,dict[str,any]]:
        def contains_template(line:str, template_names:list[str]) -> tuple[bool,str|None]:
            for template_name in template_names:
                if "\"%s\", %s" % (game_name, template_name) in line: return True, template_name # ", " is included so other things that don't actually use them don't use them.
            else: return False, None
        game_name = line.split("\"")[1]
        line_contains_template, template_name = contains_template(line, list(templates.keys()))
        if line_contains_template:
            return game_name, templates[template_name]
        else:
            sound_type = self.find_soundtype(line, sound_types, default_sound_type)
            class_extension = self.find_other_class_name(line)
            return game_name, {"sound_type": sound_type, "class_extension": class_extension}

    def remove_class_extension(self, blocks:dict[str,dict[str,any]]) -> tuple[dict[str,dict[str,any]],dict[str,str]]:
        block_other_classes:dict[str,str] = {}
        for block, properties in list(blocks.items()):
            block_other_classes[block] = properties["class_extension"]
            del properties["class_extension"]
        return blocks, block_other_classes

    def analyze_blocks(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], default_sound_type:str) -> tuple[dict[str,dict[str,any]],dict[str,str]]:
        '''Returns a dict of blocks with their dict of properties and another dict of {game_name: extended file name in Blocks.java}'''
        def should_skip_line(line:str) -> bool:
            for skip_line in SKIP_LINES:
                if line.startswith(skip_line): return True
            else: return False
        RECORD_START = "    public static void "
        RECORD_END = "        for ("
        RECORD_START_THRESHOLD = 2
        SKIP_LINES = ["        int "]
        recording_threshold = 0
        recording = False
        templates:dict[str,dict[str,any]] = {}
        blocks:dict[str,dict[str,any]] = {}
        for line_index, line in enumerate(file_contents):
            line = line.rstrip()
            next_line = file_contents[line_index + 1] if line_index < len(file_contents) - 1 else ""
            if line.startswith(RECORD_START):
                recording_threshold += 1
                if recording:
                    raise ValueError("Start recording line in Blocks in %s encountered too many times!" % version)
                if recording_threshold >= RECORD_START_THRESHOLD: recording = True
                else: continue
            elif next_line.startswith(RECORD_END) and recording: recording = False; break
            elif should_skip_line(line): continue
            elif recording:
                if "=" in line: # template
                    template_name, template_data = self.evaluate_template(line, version, sound_types, default_sound_type)
                    templates[template_name] = template_data
                else: # block
                    block_name, block_properties = self.evaluate_block(line, version, templates, sound_types, default_sound_type)
                    blocks[block_name] = block_properties
        else:
            raise ValueError("Blocks in %s did not break before end of file!" % version)
        blocks, blocks_classes = self.remove_class_extension(blocks)
        return blocks, blocks_classes

    def expand_sound_type(self, name:str) -> str:
        return "1.0 1.0 dig.%s step.%s dig.%s".replace("%s", name)
    def expand_sound_types(self, sound_types:dict[str,str]) -> dict[str,str]:
        output:dict[str,str] = {}
        for key, value in list(sound_types.items()):
            if "." not in key: output[self.expand_sound_type(key)] = value
            else: output[key] = value
        return output
    def condense_sound_type(self, sound_type:dict[str,int|str]) -> str:
        def a(name:str) -> int|str:
            '''Gets the given name from `sound_type`'''
            return str(sound_type[name])
        return " ".join([a("volume"), a("pitch"), a("dig"), a("step"), a("dig2")])

    def label_sound_types(self, sound_types:dict[str,dict[str,int|str]], default_sound_type:str, version:str) -> dict[str,str]:
        '''Creates a dict such as "slime": "q"'''
        SOUND_TYPES = { # yes this is cursed i don't care
            "wood": "wood",
            "gravel": "gravel",
            "grass": "grass",
            "1.0 1.0 dig.stone step.stone dig.stone": "stone",
            "1.0 1.5 dig.stone step.stone dig.stone": "metal",
            "1.0 1.0 dig.glass step.stone step.stone": "glass",
            "cloth": "cloth",
            "sand": "sand",
            "snow": "snow",
            "1.0 1.0 dig.wood step.ladder dig.wood": "ladder",
            "0.3 1.0 dig.stone step.anvil random.anvil_land": "anvil",
            "1.0 1.0 mob.slime.big mob.slime.small mob.slime.big": "slime"
        }
        sound_types_expanded = self.expand_sound_types(SOUND_TYPES)
        output:dict[str,str] = {}
        for sound_type_name, sound_type_properties in list(sound_types.items()):
            if sound_type_name == default_sound_type: continue
            sound_type_condensed = self.condense_sound_type(sound_type_properties)
            if sound_type_condensed not in sound_types_expanded:
                raise KeyError("Sound type %s (%s) not found in Blocks in %s!" % (sound_type_name, sound_type_condensed, version))
            output[sound_types_expanded[sound_type_condensed]] = sound_type_name
        return output

    def analyze_default_sound_type(self, file_contents:list[str], version:str) -> str:
        '''Returns the default sound type, e.g. "e"'''
        SOUND_TYPE_CLASS_DECLARER = "    public static class "
        for line in reversed(file_contents): # first pass in reverse to find class name
            line = line.rstrip()
            if line.startswith(SOUND_TYPE_CLASS_DECLARER):
                sound_type_class = line.replace(SOUND_TYPE_CLASS_DECLARER, "").split(" ")[0]
                break
        else:
            raise ValueError("analyze_default_sound_type first pass in Blocks did not find value before end of file in %s!" % version)
        default_sound_type_declarer = "    public " + sound_type_class + " "
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(default_sound_type_declarer):
                default_sound_type = line.split(" ")[-1].replace(";", "")
                if len(default_sound_type) != 1:
                    raise ValueError("Default sound type \"%s\" is not length 1 in Blocks in %s!" % (default_sound_type, version))
                elif not default_sound_type.isalpha():
                    raise ValueError("Default sound type \"%s\" is not alphabetical in Blocks in %s!" % (default_sound_type, version))
                return default_sound_type
        else:
            raise ValueError("analyze_default_sound_type second pass in Blocks did not find value before end of file in %s!" % version)

    def analyze_block_file(self, version:str, file_name:str, all_properties:dict[str,dict[str,any]], default_block_file:str, sound_types:dict[str,dict[str,int|str]]) -> dict[str,dict[str,any]]:
        def should_start_recording(line:str) -> tuple[bool, bool]:
            for record_start in RECORD_STARTS:
                if line.startswith(record_start % file_name): return True
            else: return False
        if file_name == default_block_file: raise ValueError("Accidentally got Blocks.java (\"%s\") from extension recursion in Blocks in %s!" % (default_block_file, version))
        with open(os.path.join("./_versions", version, "client_decompiled", file_name + ".java"), "rt") as f:
            file_contents = f.readlines()
        RECORD_STARTS = ["    public %s(", "    protected %s("]
        CLASS_STARTS = ["public class %s"]
        RECORD_END = "    }"
        CLASS_END = "}"
        EXTENSION_DECLARATION = "extends "
        recording = False
        if file_name not in all_properties: all_properties[file_name] = {}
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(EXTENSION_DECLARATION):
                extended_file = line.replace(EXTENSION_DECLARATION, "").split(" ")[0]
                if extended_file == default_block_file: continue
                elif extended_file not in all_properties:
                    self.analyze_block_file(version, extended_file, all_properties, default_block_file, sound_types)
                all_properties[file_name] = all_properties[extended_file]

            elif should_start_recording(line):
                if recording:
                    raise ValueError("Recording line encountered multiple times in %s.java in Blocks in %s!" % (file_name, version))
                recording = True
            elif line.startswith(RECORD_END) and recording: recording = False; break
            elif recording:
                sound_type = self.find_soundtype(line, sound_types, None, key="this.a(%s)") # default_sound_type is None so it returns None if it fails
                if sound_type is not None:
                    all_properties[file_name]["sound_type"] = sound_type
        else:
            if recording: raise ValueError("analyze_block_file in %s in Blocks in %s did not find value before end of file!" % (file_name, version))
        return all_properties

    def get_properties_from_files(self, version:str, blocks_files:dict[str,str], default_block_file:str, sound_types:dict[str,dict[str,int|str]]) -> dict[str,dict[str,any]]:
        def remove_duplicates(input_list:list) -> list:
            already = set()
            output = []
            for item in input_list:
                if item in already: continue
                else:
                    already.add(item)
                    output.append(item)
            return output
        files = remove_duplicates([file for file in list(blocks_files.values()) if file != default_block_file]) # all files except Blocks.java
        block_properties:dict[str,dict[str,any]] = {}
        for file in files:
            self.analyze_block_file(version, file, block_properties, default_block_file, sound_types)
        return DataMiner.DataMiner.sort_dict(block_properties)

    def resolve_defaults(self, blocks:dict[str,dict[str,any]], overrides:dict[str,str], default_allowances:set[str], default_sound_type:str, sound_type_labels:dict[str,str], version:str) -> dict[str,dict[str,any]]:
        for override_key, override_value in list(overrides.items()):
            if override_key not in blocks:
                raise ValueError("Block \"%s\" not in block list in Blocks in %s!" % (override_key, version))
            blocks[override_key]["sound_type"] = sound_type_labels[override_value]
        all_defaults = set([block for block, block_properties in list(blocks.items()) if block_properties["sound_type"] == default_sound_type])
        blocks_that_arent_default_but_should_be = default_allowances.difference(all_defaults)
        blocks_that_are_default_but_shouldnt_be = all_defaults.difference(default_allowances)
        if (should_be := len(blocks_that_arent_default_but_should_be)) > 0 or (shouldnt_be := len(blocks_that_are_default_but_shouldnt_be)) > 0:
            error_message = "In Blocks in %s:" % version
            if should_be > 0:
                error_message += "\nThe following blocks should have the default sound type, but don't: %s" % ", ".join(blocks_that_arent_default_but_should_be)
            if shouldnt_be > 0:
                error_message += "\nThe following blocks should not have the default sound type, but do: %s" % ", ".join(blocks_that_are_default_but_shouldnt_be)
            raise KeyError(error_message)
        return blocks

    def analyze(self, blocks_file_contents:list[str], blocks_list_file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]]) -> dict[str,dict[str,any]]:
        # The code gets super wonky. I had to do it. (referring to SOUND_TYPE_OVERRIDES and SOUND_TYPE_DEFAULT_ALLOWS)
        # NOTE: redstone wire is explicitly defined as default sound type
        SOUND_TYPE_OVERRIDES = self.sound_type_overrides
        SOUND_TYPE_DEFAULT_ALLOWS = set(["air", "flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "barrier"])
        default_sound_type = self.analyze_default_sound_type(blocks_file_contents, version)
        blocks, blocks_other_files = self.analyze_blocks(blocks_file_contents, version, sound_types, default_sound_type)
        blocks_code_names, blocks_files, default_block_file = self.analyze_block_list(blocks_list_file_contents, version)
        properties_from_files = self.get_properties_from_files(version, blocks_other_files, default_block_file, sound_types)
        for game_name, code_name in list(blocks_code_names.items()):
            blocks[game_name]["code_name"] = code_name
        for file_name, properties in list(properties_from_files.items()):
            for property_name, property_value in list(properties.items()):
                for game_name, block_file in list(blocks_other_files.items()):
                    if block_file == file_name: blocks[game_name][property_name] = property_value
        sound_type_labels = self.label_sound_types(sound_types, default_sound_type, version)
        blocks = self.resolve_defaults(blocks, SOUND_TYPE_OVERRIDES, SOUND_TYPE_DEFAULT_ALLOWS, default_sound_type, sound_type_labels, version)
        return blocks

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        blocks_list_file = self.search_blocks_list(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_list_file), "rt") as f:
            blocks_list_file_contents = f.readlines()
        sound_types = SoundType.get_data_file(version)
        blocks = self.analyze(blocks_file_contents, blocks_list_file_contents, version, sound_types)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

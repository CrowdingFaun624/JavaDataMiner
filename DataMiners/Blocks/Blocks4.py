import os

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks4(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.blocks_record_threshold = 2
        self.blocks_list_record_threshold = 1
        self.sound_type_overrides = {"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "acacia_stairs": "wood", "dark_oak_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone", "red_sandstone_stairs": "stone"}
        self.sound_type_allowances = ["air", "flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "barrier"]
        self.sound_type_shut_up = []
        self.sound_type_class_name_getter_mode = 0
        self.next_line_look_ahead = 1
        self.search_mode = 0
        self.sound_types_condensed = {"wood": "wood", "gravel": "gravel", "grass": "grass", "1.0 1.0 dig.stone step.stone dig.stone": "stone", "1.0 1.5 dig.stone step.stone dig.stone": "metal","1.0 1.0 dig.glass step.stone step.stone": "glass","cloth": "cloth", "sand": "sand", "snow": "snow", "1.0 1.0 dig.wood step.ladder dig.wood": "ladder", "0.3 1.0 dig.stone step.anvil random.anvil_land": "anvil", "1.0 1.0 mob.slime.big mob.slime.small mob.slime.big": "slime"}
        self.skip_blocks = []
        if "blocks_record_threshold" in kwargs:
            self.blocks_record_threshold = kwargs["blocks_record_threshold"]
        if "blocks_list_record_threshold" in kwargs:
            self.blocks_list_record_threshold = kwargs["blocks_list_record_threshold"]
        if "sound_type_overrides" in kwargs:
            self.sound_type_overrides = kwargs["sound_type_overrides"]
        if "sound_type_allowances" in kwargs:
            self.sound_type_allowances = kwargs["sound_type_allowances"]
        if "sound_type_shut_up" in kwargs:
            self.sound_type_shut_up = kwargs["sound_type_shut_up"] # prevents a block from showing default-related error messages
        if "sound_type_class_name_getter_mode" in kwargs:
            self.sound_type_class_name_getter_mode = kwargs["sound_type_class_name_getter_mode"]
        if "next_line_look_ahead" in kwargs:
            self.next_line_look_ahead = kwargs["next_line_look_ahead"]
        if "search_mode" in kwargs:
            self.search_mode = kwargs["search_mode"]
        if "sound_types_condensed" in kwargs:
            self.sound_types_condensed = kwargs["sound_types_condensed"]
        if "skip_blocks" in kwargs:
            self.skip_blocks = kwargs["skip_blocks"]
    
    def search_blocks(self, version:str) -> str:
        '''Returns the file path of Blocks.java (e.g. art.java)'''
        SEARCH_PARAMETERS = [["stone", "grass", "leaves", "dispenser", "not:name_tag", "not:Bootstrap", "float"], 
                             ["stone", "grass", "leaves", "dispenser", "\".name\""]][self.search_mode]
        blocks_files = Searcher.search(version, "client", SEARCH_PARAMETERS, set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def search_blocks_list(self, version:str) -> str:
        '''Returns the file path of BlocksList.java (e.g. aru.java)'''
        SEARCH_PARAMETERS = [["stone", "grass", "leaves", "dispenser", "not:name_tag", "Bootstrap"],
                             ["stone", "grass", "leaves", "dispenser", "not:.name"]][self.search_mode]
        blocks_files = Searcher.search(version, "client", SEARCH_PARAMETERS, set(["and"]))
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
        RECORD_START = {0: "        }", 1: "public class "}[self.search_mode]
        RECORD_END = {0: "    }", 1: "}"}[self.search_mode]
        DEFAULT_FILE_DECLARATION = "    private static "
        DEFAULT_FILE_GIVE_UP1 = "        }"
        CONTINUES = ["ashSet", ".clear();"]
        CODE_NAME_POSITION = {0: 0, 1: 1}[self.search_mode]
        DIFFERENT_FILE_POSITION = {0: 2, 1: 3}[self.search_mode]
        recording = False
        default_file_strategy = {0: 0, 1: 1}[self.search_mode]
        start_threshold = 0
        names:dict[str,str] = {}
        files:dict[str,str] = {}
        default_file = None
        for line in file_contents:
            line = line.rstrip()
            if should_continue(line): continue
            elif line.startswith(DEFAULT_FILE_DECLARATION) and default_file_strategy == 0:
                default_file = line.replace(DEFAULT_FILE_DECLARATION, "").split(" ")[0]
            elif line.startswith(RECORD_START):
                if default_file is None and line.startswith(DEFAULT_FILE_GIVE_UP1) and default_file_strategy == 0: default_file_strategy += 1; default_file = None
                if recording:
                    raise ValueError("Recording line encountered multiple times in Blocks in %s!" % version)
                start_threshold += 1
                if start_threshold >= self.blocks_list_record_threshold: recording = True
            elif (line.startswith(RECORD_END) or line == "") and recording: recording = False; break
            elif recording:
                if "\"" not in line: raise ValueError("Line \"%s\" in BlocksList in %s is wonky (search mode %s)!" % (line.lstrip(), version, self.search_mode))
                split_line = line.lstrip().split(" ")
                code_name = line.lstrip().replace("    public static final ", "").split(" ")[CODE_NAME_POSITION]
                game_name = line.split("\"")[-2]
                if default_file_strategy == 1:
                    new_default_file = line.split(")")[1].split(".")[0]
                    if default_file is None: default_file = new_default_file
                    elif default_file != new_default_file: raise ValueError("BlocksList has inconsistent default file in %s: \"%s\" does not match \"%s\"!" % (version, new_default_file, default_file))
                has_different_file = split_line[DIFFERENT_FILE_POSITION].startswith("(")
                if has_different_file:
                    if self.search_mode == 0: file = split_line[2].split(")")[0][1:]
                    elif self.search_mode == 1: file = split_line[0]
                else: file = default_file
                names[game_name] = code_name
                files[game_name] = file
        else: # if code did not break before end of file
            raise ValueError("BlocksList in %s did not stop recording/start recording before end of file!" % version)
        if default_file is None: raise ValueError("Did not find default file before end of file in BlocksList in %s!" % version)
        return names, files, default_file

    def find_soundtype(self, line:str, sound_types:dict[str,dict[str,int|str]], default_sound_type:str, blocks_file_name:str, version:str, keys:list[str]|None=None) -> str|None:
        '''Returns a soundtype from a line, e.g. "i", "g" or "b".'''
        def get_sound_type_text(sound_type:str) -> list[str]:
            output:list[str] = []
            for key in keys:
                key_count = key.count("%s")
                if key_count == 1:
                    output.append(key % sound_type)
                elif key_count == 2:
                    output.append(key % (blocks_file_name, sound_type))
                else: raise ValueError("Wonky key in find_soundtype in Blocks in %s: \"%s\"" % (version, key))
            return output
        def is_in(sound_type_texts:list[str], line:str) -> bool:
            for sound_type_text in sound_type_texts:
                if sound_type_text in line: return True
            else: return False
        keys = [".a(%s)", ".a(%s.%s)"]
        for sound_type in list(sound_types.keys()):
            sound_type_texts = get_sound_type_text(sound_type) # "a" is not a variable because there should only be one function with an input of a soundtype
            if is_in(sound_type_texts, line): return sound_type
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

    def evaluate_template(self, line:str, version:str, sound_types:dict[str,dict[str,int|str]], default_sound_type:str, blocks_file_name:str) -> tuple[str,dict[str,any]]:
        split_line = line.lstrip().split(" ")
        if split_line[1] == "=":
            template_name = split_line[0]
        elif split_line[2] == "=":
            template_name = split_line[1]
        else: raise ValueError("\"=\" in Blocks in %s is in a weird position in line \"%s\"" % (version, line))
        sound_type = self.find_soundtype(line, sound_types, None, blocks_file_name, version)
        class_extension = self.find_other_class_name(line)
        return template_name, self.remove_nones({"sound_type": sound_type, "class_extension": class_extension})

    def evaluate_block(self, line:str, version:str, templates:dict[str,dict[str,any]], sound_types:dict[str,dict[str,int|str]], default_sound_type:str, blocks_file_name:str) -> tuple[str,dict[str,any]]:
        def contains_template(line:str, template_names:list[str]) -> tuple[bool,str|None]:
            for template_name in template_names:
                if "\"%s\", %s" % (game_name, template_name) in line: return True, template_name # ", " is included so other things that don't actually use them don't use them.
            else: return False, None
        game_name = line.split("\"")[1]
        line_contains_template, template_name = contains_template(line, list(templates.keys()))
        if line_contains_template:
            return game_name, templates[template_name]
        else:
            sound_type = self.find_soundtype(line, sound_types, default_sound_type, blocks_file_name, version)
            class_extension = self.find_other_class_name(line)
            return game_name, {"sound_type": sound_type, "class_extension": class_extension}

    def remove_class_extension(self, blocks:dict[str,dict[str,any]]) -> tuple[dict[str,dict[str,any]],dict[str,str]]:
        block_other_classes:dict[str,str] = {}
        for block, properties in list(blocks.items()):
            block_other_classes[block] = properties["class_extension"]
            del properties["class_extension"]
        return blocks, block_other_classes

    def analyze_blocks(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], default_sound_type:str, blocks_file_name:str) -> tuple[dict[str,dict[str,any]],dict[str,str]]:
        '''Returns a dict of blocks with their dict of properties and another dict of {game_name: extended file name in Blocks.java}'''
        def should_skip_line(line:str) -> bool:
            for skip_line in SKIP_LINES:
                if line.startswith(skip_line): return True
            else: return False
        RECORD_START = "    public static void "
        RECORD_END = "        for ("
        RECORD_START_THRESHOLD = self.blocks_record_threshold
        SKIP_LINES = ["        int "]
        NEXT_LINE_LOOK_AHEAD = self.next_line_look_ahead
        recording_threshold = 0
        recording = False
        templates:dict[str,dict[str,any]] = {}
        blocks:dict[str,dict[str,any]] = {}
        for line_index, line in enumerate(file_contents):
            line = line.rstrip()
            next_line = file_contents[line_index + NEXT_LINE_LOOK_AHEAD] if line_index < len(file_contents) - NEXT_LINE_LOOK_AHEAD else ""
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
                    template_name, template_data = self.evaluate_template(line, version, sound_types, default_sound_type, blocks_file_name)
                    templates[template_name] = template_data
                else: # block
                    block_name, block_properties = self.evaluate_block(line, version, templates, sound_types, default_sound_type, blocks_file_name)
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
        SOUND_TYPES = self.sound_types_condensed
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
        if self.sound_type_class_name_getter_mode == 0:
            SOUND_TYPE_CLASS_DECLARER = "    public static class "
            for line in reversed(file_contents): # first pass in reverse to find class name
                line = line.rstrip()
                if line.startswith(SOUND_TYPE_CLASS_DECLARER):
                    sound_type_class = line.replace(SOUND_TYPE_CLASS_DECLARER, "").split(" ")[0]
                    break
            else: raise ValueError("analyze_default_sound_type first pass in Blocks did not find value before end of file in %s!" % version)
        elif self.sound_type_class_name_getter_mode == 1:
            SOUND_TYPE_DECLARER = "    public static final " # and contains """
            END_RECORDING = "    protected "
            sound_type_class = None
            for line in file_contents:
                line = line.rstrip()
                if line.startswith(SOUND_TYPE_DECLARER) and "\"" in line and "\"air\"" not in line:
                    new_sound_type_class = line.replace(SOUND_TYPE_DECLARER, "").split(" ")[0]
                    if sound_type_class is None: sound_type_class = new_sound_type_class
                    elif sound_type_class != new_sound_type_class:
                        raise ValueError("SoundType base class %s does not match %s in SoundType.Blocks (pass 1) in %s!" % (sound_type_class, new_sound_type_class, version))
                if line.startswith(END_RECORDING) and sound_type_class is not None: break
            else: raise ValueError("analyze_default_sound_type first pass in Blocks did not find value before end of file in %s!" % version)
        else: raise ValueError("Invalid \"sound_type_class_name_getter_mode\" parameter (%s) in Blocks4 was given in %s!" % (self.sound_type_class_name_getter_mode, version))
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

    def analyze_block_file(self, version:str, file_name:str, all_properties:dict[str,dict[str,any]], default_block_file:str, sound_types:dict[str,dict[str,int|str]], blocks_file_name:str) -> dict[str,dict[str,any]]:
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
                    self.analyze_block_file(version, extended_file, all_properties, default_block_file, sound_types, blocks_file_name)
                all_properties[file_name] = all_properties[extended_file]

            elif should_start_recording(line):
                if recording:
                    raise ValueError("Recording line encountered multiple times in %s.java in Blocks in %s!" % (file_name, version))
                recording = True
            elif line.startswith(RECORD_END) and recording: recording = False; break
            elif recording:
                sound_type = self.find_soundtype(line, sound_types, None, blocks_file_name, version, keys=["this.a(%s)","this.a(%s.%s)"]) # default_sound_type is None so it returns None if it fails
                if sound_type is not None:
                    all_properties[file_name]["sound_type"] = sound_type
        else:
            if recording: raise ValueError("analyze_block_file in %s in Blocks in %s did not find value before end of file!" % (file_name, version))
        return all_properties

    def get_properties_from_files(self, version:str, blocks_files:dict[str,str], default_block_file:str, sound_types:dict[str,dict[str,int|str]], blocks_file_name:str) -> dict[str,dict[str,any]]:
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
            self.analyze_block_file(version, file, block_properties, default_block_file, sound_types, blocks_file_name)
        return DataMiner.DataMiner.sort_dict(block_properties)

    def resolve_defaults(self, blocks:dict[str,dict[str,any]], overrides:dict[str,str], default_allowances:set[str], shut_ups:set[str], default_sound_type:str, sound_type_labels:dict[str,str], version:str) -> dict[str,dict[str,any]]:
        def remove_from_set(set1:set, set2:set) -> set:
            '''Removes items from set1 that are in set2'''
            for item in set2:
                if item in set1: set1.remove(item)
            return set1
        bad_blocks:list[str] = []
        for override_key, override_value in list(overrides.items()):
            if override_key not in blocks: bad_blocks.append(override_key); continue
                #raise ValueError("Block \"%s\" not in block list in Blocks in %s!" % (override_key, version))
            blocks[override_key]["sound_type"] = sound_type_labels[override_value]
        if len(bad_blocks) > 0: raise ValueError("The following blocks were not in block list in Blocks in %s: %s" % (version, ", ".join(bad_blocks)))
        all_defaults = set([block for block, block_properties in list(blocks.items()) if block_properties["sound_type"] == default_sound_type])
        blocks_that_arent_default_but_should_be = remove_from_set(default_allowances.difference(all_defaults), shut_ups)
        blocks_that_are_default_but_shouldnt_be = remove_from_set(all_defaults.difference(default_allowances), shut_ups)
        should_be = len(blocks_that_arent_default_but_should_be)
        shouldnt_be = len(blocks_that_are_default_but_shouldnt_be)
        if should_be > 0 or shouldnt_be > 0:
            error_message = "In Blocks in %s:" % version
            if should_be > 0:
                error_message += "\nThe following blocks should have the default sound type, but don't: %s" % ", ".join(blocks_that_arent_default_but_should_be)
            if shouldnt_be > 0:
                error_message += "\nThe following blocks should not have the default sound type, but do: %s" % ", ".join(blocks_that_are_default_but_shouldnt_be)
            raise KeyError(error_message)
        return blocks

    def analyze(self, blocks_file_contents:list[str], blocks_list_file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], blocks_file_name:str) -> dict[str,dict[str,any]]:
        # The code gets super wonky. I had to do it. (referring to SOUND_TYPE_OVERRIDES and SOUND_TYPE_DEFAULT_ALLOWS)
        # NOTE: redstone wire is explicitly defined as default sound type
        SOUND_TYPE_OVERRIDES = self.sound_type_overrides
        SOUND_TYPE_DEFAULT_ALLOWS = set(self.sound_type_allowances)
        SOUND_TYPE_SHUT_UP = set(self.sound_type_shut_up)
        default_sound_type = self.analyze_default_sound_type(blocks_file_contents, version)
        blocks, blocks_other_files = self.analyze_blocks(blocks_file_contents, version, sound_types, default_sound_type, blocks_file_name)
        blocks_code_names, blocks_files, default_block_file = self.analyze_block_list(blocks_list_file_contents, version)
        properties_from_files = self.get_properties_from_files(version, blocks_other_files, default_block_file, sound_types, blocks_file_name)
        SKIP_BLOCKS = set(self.skip_blocks)
        for game_name, code_name in list(blocks_code_names.items()): # i am resisting the urge to do if version == "13w41b" and game_name = "chest_locked...": continue
            if game_name in SKIP_BLOCKS: continue
            blocks[game_name]["code_name"] = code_name
        for file_name, properties in list(properties_from_files.items()):
            for property_name, property_value in list(properties.items()):
                for game_name, block_file in list(blocks_other_files.items()):
                    if block_file == file_name: blocks[game_name][property_name] = property_value
        sound_type_labels = self.label_sound_types(sound_types, default_sound_type, version)
        blocks = self.resolve_defaults(blocks, SOUND_TYPE_OVERRIDES, SOUND_TYPE_DEFAULT_ALLOWS, SOUND_TYPE_SHUT_UP, default_sound_type, sound_type_labels, version)
        return blocks

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search_blocks(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        try:
            blocks_list_file = self.search_blocks_list(version)
        except (FileExistsError, FileNotFoundError): # thsi fricker switches every two versions I can't stand it.
            self.search_mode = 1
            blocks_list_file = self.search_blocks_list(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_list_file), "rt") as f:
            blocks_list_file_contents = f.readlines()
        sound_types = SoundType.SoundType.get_data_file(version)
        if sound_types == {}: raise ValueError("SoundTypes returned empty dict in Blocks in %s!" % version)
        blocks = self.analyze(blocks_file_contents, blocks_list_file_contents, version, sound_types, blocks_file.split(".")[0])
        if store: self.store(version, blocks, "blocks.json")
        return blocks

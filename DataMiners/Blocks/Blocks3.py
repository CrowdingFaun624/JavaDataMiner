import os
from typing import Any

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks3(DataMiner.DataMiner):
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

    def get_sound_type_name(self, sound_type_content:dict[str,int|str], version:str) -> str: # TODO: this is duplicated in Blocks1, please fix.
        def is_only_one(input_list:list[str]) -> tuple[bool, str|None]:
            '''Tests if the list contains only the same item, and returns (True, <item>) if so and (False, None) if not.'''
            input_set = set(input_list)
            if len(input_set) == 1: return True, input_list[0]
            else: return False, None
        sound_events = [sound_type_content[index] for index in ["break", "step", "place", "hit", "fall"]]
        for sound_event in sound_events:
            if not sound_event.count(".") == 2: raise ValueError("Incorrect number of periods in sound type in Blocks process in %s: %s" % (version, str(sound_events)))
        sound_events = [sound_event.split(".")[1] for sound_event in sound_events]
        is_same = is_only_one(sound_events)
        if is_same[0]:
            return is_same[1].upper()
        else:
            return " ".join(sound_events).upper()
    
    def get_stone_name(self, sound_types:dict[str,dict[str,int|str]], version:str) -> str: # TODO: also duplicated in Blocks1
        '''Gets the code name of stone'''
        stone_key = "STONE"
        for sound_type_code_name, sound_type_content in list(sound_types.items()):
            if self.get_sound_type_name(sound_type_content, version) == stone_key:
                return sound_type_code_name
        else: raise ValueError("No sound type of %s exists for Blocks in %s!" % (stone_key, version))

    def get_template_id(self, line:str, version:str) -> tuple[int, str]:
        '''Gets the integer id of the template on the line and the character after the id'''
        if "\\u" not in line: raise ValueError("The given line \"%s\" in Blocks in %s does not have \"\\u\"!" % (line, version))
        template_id = line.split("\\u")[1]
        output = ""
        for char in template_id: # adds digit characters to the output until it isn't and then exits
            if char.isdigit(): output += char
            else: last_char = char; break
        return int(output), last_char

    def evaluate_block(self, line:str, version:str, templates:dict[int,dict[str,Any]], sound_types:dict[str,dict[str,int|str]], sound_types_name:str, stone_code_name:str, most_recent_template:dict[str,Any], template_id_constant:int) -> tuple[str, dict[str,Any]]:
        '''Returns the block's name and its properties'''
        ALLOWED_NO_PROPERTIES = ["brick_stairs", "nether_brick_stairs", "purpur_stairs"] # blocks that have no properties for some reason.
        def defaults() -> tuple[str,str]:
            return "STONE", stone_code_name
        game_name = line.split("\"")[1]
        if sound_types_name + "." in line:
            sound_type_code_name = line.split("(" + sound_types_name + ".")[-1].split(")")[0]
            sound_type_contents = sound_types[sound_type_code_name]
            sound_type = self.get_sound_type_name(sound_type_contents, version)
        elif "\\u" in line:
            template_id, character_after = self.get_template_id(line, version)
            if template_id != template_id_constant: raise ValueError("Template id \"%s\" is not the constant \"%s\" in Blocks in %s" % (template_id, template_id_constant, version))
            if character_after == ".":
                template_name = line.split("\\u")[1].split("(")[2].split(".")[0]
                if any([x in template_name for x in "\\;\"()"]): # weird case like on brick_stairs
                    sound_type, sound_type_code_name = defaults()
                    template_data = None
                    if game_name not in ALLOWED_NO_PROPERTIES: raise ValueError("Block \"%s\" has no properties in Blocks in %s!" % (game_name, version))
                elif template_name not in templates: raise KeyError("Template \"%s\" is not a known template in Blocks in %s!" % (template_name, version))
                else: template_data = templates[template_name]
            else:
                if most_recent_template is None: raise UnboundLocalError("Template \"%s\" was used before being declared in Blocks in %s!" % (template_id, version))
                template_data = most_recent_template
            if template_data is not None and "sound_type" in template_data:
                sound_type = template_data["sound_type"]
                sound_type_code_name = template_data["sound_type_code_name"]
            else: sound_type, sound_type_code_name = defaults()
        else: sound_type, sound_type_code_name = defaults()
        return game_name, {"sound_type": sound_type, "sound_type_code_name": sound_type_code_name}

    def evaluate_template(self, line:str, version:str, sound_types:dict[str,dict[str,int|str]], sound_types_name:str, stone_code_name:str) -> tuple[str, int, dict[str,Any]]:
        '''Returns the template's id and its properties'''
        def defaults() -> tuple[str,str]:
            return "STONE", stone_code_name
        template_id = self.get_template_id(line, version)[0]
        template_name = line.split("new ")[1].split("(")[0]
        if sound_types_name + "." in line:
            sound_type_code_name = line.split("(" + sound_types_name + ".")[-1].split(")")[0]
            sound_type_contents = sound_types[sound_type_code_name]
            sound_type = self.get_sound_type_name(sound_type_contents, version)
        else: sound_type, sound_type_code_name = defaults()
        return template_name, template_id, {"sound_type": sound_type, "sound_type_code_name": sound_type_code_name}

    def analyze_block_list(self, file_contents:list[str], version:str) -> dict[str,str]:
        '''Returns a dict of `{game name: code_name}`.'''
        RECORD_START = "newHashSet" # contains
        RECORD_END = ".clear();" # contains
        recording = False
        output:dict[str,str] = {}
        for line in file_contents:
            line = line.rstrip()
            if RECORD_START in line:
                if recording:
                    raise ValueError("Start recording line encountered twice for BlocksList in %s!" % version)
                recording = True
            elif RECORD_END in line and recording: break
            else:
                if not recording: continue
                stripped_line = line.strip()
                code_name = stripped_line.split(" ")[0]
                game_name = stripped_line.split("\"")[-2]
                output[game_name] = code_name
        else:
            if not recording: raise ValueError("Start recording line never encountered in BlocksList in %s!" % version)
            raise ValueError("Recording line not encountered in BlocksList in %s!" % version)
        return output

    def analyze_blocks(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], sound_types_name:str) -> dict[str,dict[str,Any]]:
        RECORD_START = "    public static void "
        RECORD_START_THRESHOLD = 2 # how many RECORD_STARTs must occur to start recording
        RECORD_END = "        for ("
        recording_threshold = 0
        recording = False
        stone_code_name = self.get_stone_name(sound_types, version)
        template_id_constant = None
        most_recent_template = None
        output:dict[str,dict[str,Any]] = {}
        templates:dict[int,dict[str,Any]] = {} # stores the \u26034 things
        LINE_VALID_TABLE = {(False,False,False):False,(False,False,True):False,(False,True,False):False,(False,True,True):True,
                            (True,False,False):True,(True,False,True):False,(True,True,False):True,(True,True,True):True}
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(RECORD_START):
                if recording:
                    raise ValueError("Start recording line encountered %s times for Blocks in %s!" % (RECORD_START_THRESHOLD + 1, version))
                recording_threshold += 1
                if recording_threshold == RECORD_START_THRESHOLD: recording = True
                elif recording_threshold > RECORD_START_THRESHOLD: raise ValueError("Something has gone wrong in Blocks in %s!" % version)
            elif line.startswith(RECORD_END) and recording: break
            else:
                if not recording: continue
                if not LINE_VALID_TABLE[("\"" in line, "\\u" in line, "=" in line)]: continue # removes weird lines at beginning
                line_stripped = line.strip()
                line_split = line_stripped.split(" ")
                if "." in line_split[0]: # block declaration
                    block_name, block_properties = self.evaluate_block(line_stripped, version, templates, sound_types, sound_types_name, stone_code_name, most_recent_template, template_id_constant)
                    output[block_name] = block_properties
                else: #                  # template declaration
                    template_name, template_id, template_properties = self.evaluate_template(line_stripped, version, sound_types, sound_types_name, stone_code_name)
                    if template_id_constant is None: template_id_constant = template_id
                    if template_id != template_id_constant: raise ValueError("Template id \"%s\" is not the constant \"%s\" in Blocks in %s" % (template_id, template_id_constant, version))
                    most_recent_template = template_properties
                    templates[template_name] = template_properties
        else:
            if not recording: raise ValueError("Start recording line never encountered in Blocks in %s!" % version)
            raise ValueError("Recording line not encountered in Blocks in %s!" % version)
        return output

    def analyze(self, blocks_file_contents:list[str], blocks_list_file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], sound_types_name:str) -> dict[str,dict[str,Any]]:
        blocks = self.analyze_blocks(blocks_file_contents, version, sound_types, sound_types_name)
        blocks_code_names:dict[str,str] = self.analyze_block_list(blocks_list_file_contents, version)
        blocks_set = set(list(blocks.keys())); blocks_list_set = set(list(blocks_code_names.keys()))
        if (set_difference := (blocks_set - blocks_list_set).union(blocks_list_set - blocks_set)) != set():
            print(", ".join(list(set_difference)))
            raise KeyError("Blocks and BlocksList have different keys in %s!" % version)
        for block_game_name, block_code_name in list(blocks_code_names.items()):
            blocks[block_game_name]["code_name"] = block_code_name
        return blocks

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,Any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        blocks_list_file = self.search_blocks_list(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_list_file), "rt") as f:
            blocks_list_file_contents = f.readlines()
        sound_types = SoundType.SoundType.get_data_file(version)
        sound_type_name = DataMiner.get_file_name_from_path(DataMiner.get_dataminer(version, SoundType.dataminers, "sound_type").search(version)) # name of SoundType.java
        blocks = self.analyze(blocks_file_contents, blocks_list_file_contents, version, sound_types, sound_type_name)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

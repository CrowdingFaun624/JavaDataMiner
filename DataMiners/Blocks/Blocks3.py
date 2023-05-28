import os

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks3(DataMiner.DataMiner):

    def search(self, version:str) -> str:
        '''Returns the file path of Blocks.java (e.g. bcs.java)'''
        blocks_files = Searcher.search(version, "client", ["stone", "grass", "leaves", "dispenser", "not:name_tag", "not:Bootstrap"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def search_blocks_list(self, version:str) -> str:
        '''Returns the file path of BlocksList.java (e.g. bct.java)'''
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
        sound_blocks = [sound_event.split(".")[1] for sound_event in sound_events]
        is_same = is_only_one(sound_blocks)
        if is_same[0]:
            return is_same[1].upper()
        else:
            return " ".join(sound_blocks).upper()
    
    def get_stone_name(self, sound_types:dict[str,dict[str,int|str]], version:str) -> str: # TODO: also duplicated in Blocks1
        '''Gets the code name of stone'''
        for sound_type_code_name, sound_type_content in list(sound_types.items()):
            if self.get_sound_type_name(sound_type_content, version) == "STONE":
                return sound_type_code_name
        else: raise ValueError("No sound type of STONE exists for Blocks in %s!" % version)

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

    def analyze_blocks(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], sound_types_name:str) -> dict[str,dict[str,any]]:
        pass

    def analyze(self, blocks_file_contents:list[str], blocks_list_file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], sound_types_name:str) -> dict[str,dict[str,any]]:
        blocks = self.analyze_blocks(blocks_file_contents, version, sound_types, sound_types_name)
        blocks_code_names:dict[str,str] = self.analyze_block_list(blocks_list_file_contents, version)
        blocks_set = set(list(blocks.keys())); blocks_list_set = set(list(blocks_code_names.keys()))
        if (set_difference := (blocks_set - blocks_list_set).union(blocks_list_set - blocks_set)) != set():
            print(", ".join(list(set_difference)))
            raise KeyError("Blocks and BlocksList have different keys in %s!" % version)
        for block_game_name, block_code_name in list(blocks_code_names.items()):
            blocks[block_game_name]["code_name"] = block_code_name
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
        sound_type_name = DataMiner.get_file_name_from_path(DataMiner.get_dataminer(version, SoundType.dataminers).search(version)) # name of SoundType.java
        blocks = self.analyze(blocks_file_contents, blocks_list_file_contents, version, sound_types, sound_type_name)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

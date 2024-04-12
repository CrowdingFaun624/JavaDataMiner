import os
from typing import Any

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks1(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the file path of Blocks.java'''
        blocks_files = Searcher.search(version, "client", ["air", "stone", "granite", "polished_granite", "not:##", "not:hash", "not:Hash", "not:Properties"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def get_blocks_class_name(self, file_contents:list[str], version:str) -> str:
        '''Returns the obfuscated class name of Blocks.java, e.g. "bob"'''
        CLASS_DECLARER = "public class "
        for line in file_contents:
            if line.startswith(CLASS_DECLARER):
                class_name = line.split(" ")[-2]
                return class_name
        else: raise ValueError("Unable to find class name of \"Blocks.java\" for version %s!" % version)

    def get_block_class_name(self, file_contents:list[str], version:str) -> tuple[str,str]:
        '''Returns the obfuscated class name of Block.java, e.g. "boa" and the function in Blocks.java used to declare a block'''
        FUNCTION_DECLARER = "    private static "
        for line in file_contents:
            if line.startswith(FUNCTION_DECLARER):
                stripped_line = line.replace(FUNCTION_DECLARER, "").split(" ")
                block_class_name = stripped_line[0]
                block_declarer = stripped_line[1].split("(")[0]
                return block_class_name, block_declarer
        else: raise ValueError("Unable to find class name of \"Block.java\" and block declarer function for version %s!" % version)

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

    def get_stone_name(self, sound_types:dict[str,dict[str,int|str]], version:str) -> str: # TODO: also duplicated in Blocks2
        '''Gets the code name of stone'''
        for sound_type_code_name, sound_type_content in list(sound_types.items()):
            if self.get_sound_type_name(sound_type_content, version) == "STONE":
                return sound_type_code_name
        else: raise ValueError("No sound type of STONE exists for Blocks in %s!" % version)

    def analyze(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], sound_type_name:str) -> dict[str,dict[str,Any]]:
        RECORDING_START = "public class "
        RECORDING_END = ""
        BLOCK_DECLARER = "public static final "
        recording = False
        output:dict[str,dict[str,Any]] = {}
        stone_code_name = self.get_stone_name(sound_types, version)
        for line in file_contents:
            line = line.strip()
            if line.startswith(RECORDING_START):
                if recording: raise ValueError("Start recording line encountered twice for Blocks in %s!" % version)
                recording = True
            elif line == RECORDING_END and recording: recording = False; break
            else:
                if not recording: continue
                if not line.startswith(BLOCK_DECLARER):
                    raise ValueError("Strange line encountered in Blocks for %s: \"%s\"" % (version, line))
                stripped_line = line.replace(BLOCK_DECLARER, "")
                code_name = stripped_line.split(" ")[1]
                game_name = stripped_line.split("\"")[1]
                if "(" + sound_type_name + "." in stripped_line:
                    sound_type_code_name = stripped_line.split(sound_type_name + ".")[1].split(")")[0].split(".")[0]
                    sound_type_contents = sound_types[sound_type_code_name]
                    sound_type = self.get_sound_type_name(sound_type_contents, version)
                else: sound_type = "STONE"; sound_type_code_name = stone_code_name
                output[game_name] = {"code_name": code_name, "sound_type": sound_type, "sound_type_code_name": sound_type_code_name}
        return output

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,Any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        sound_types = SoundType.SoundType.get_data_file(version)
        sound_type_name = DataMiner.get_file_name_from_path(DataMiner.get_dataminer(version, SoundType.dataminers, "sound_type").search(version)) # name of SoundType.java
        blocks = self.analyze(blocks_file_contents, version, sound_types, sound_type_name)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

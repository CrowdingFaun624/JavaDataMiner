import os

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks7(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.sound_type_allowances:list[int] = []
        if "sound_type_allowances" in kwargs:
            self.sound_type_allowances = kwargs["sound_type_allowances"]

    def search(self, version:str) -> str:
        '''Returns the file path of Blocks.java (e.g. nq.java)'''
        blocks_files = Searcher.search(version, "client", ["stone"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def try_to_find_sound_type(self, line:str, sound_types:dict[str,dict[str,int|str]]) -> str|None:
        KEY = ".a(%s)"
        strings_to_test:list[tuple[str,str]] = [(sound_type_name, KEY % sound_type_name) for sound_type_name in sound_types]
        for sound_type, string_to_test in strings_to_test:
            if string_to_test in line: return sound_type
        else: return None

    def get_copy(self, line:str, blocks:dict[str,dict[str,any]], block_id:int) -> str|None:
        output = line.split(", ")[1].split(")")[0]
        if self.get_block_with_code_name(blocks, output, None, False) is not None: return output
        else: return None

    def get_block_with_code_name(self, blocks:dict[int,dict[str,any]], code_name:str, version:str, error_on_none:bool=True) -> int|None:
        for block_id, block_properties in list(blocks.items()):
            if block_properties["code_name"] == code_name: return block_id
        else:
            if error_on_none: raise KeyError("Unable to find block with code name \"%s\" in Blocks in %s!" % (code_name, version))
            else: return None

    def analyze(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]]) -> dict[int,dict[str,any]]:
        BLOCK_DECLARER = "    public static final "
        NULL_DECLARER = "null;"
        MAGIC_NUMBER = str(256)
        recording = False
        has_met_magic_number = False
        default_sound_type = self.analyze_default_sound_type(file_contents, version, sound_types)
        output:dict[int,dict[str,any]] = {}
        for line in file_contents:
            line = line.rstrip()
            if not recording and MAGIC_NUMBER in line:
                has_met_magic_number = True
            elif not recording and has_met_magic_number and MAGIC_NUMBER not in line:
                recording = True
            elif recording:
                if not line.startswith(BLOCK_DECLARER): break
                elif line.endswith(NULL_DECLARER): continue
                block_id = line.split("new ")[1].split("(")[1].split(",")[0].split(")")[0]
                if not block_id.isdigit(): raise ValueError("Line \"%s\" in Blocks in %s created an invalid block id!" % (line, version))
                else: block_id = int(block_id)
                code_name = line.replace(BLOCK_DECLARER, "").split(" ")[1]
                sound_type = self.try_to_find_sound_type(line, sound_types)
                if sound_type is None:
                    copy_block_code_name = self.get_copy(line, output, block_id)
                    if copy_block_code_name is None: sound_type = None
                    else:
                        copy_block_id = self.get_block_with_code_name(output, copy_block_code_name, version)
                        sound_type = output[copy_block_id]["sound_type"]
                output[block_id] = {"code_name": code_name, "sound_type": sound_type}
        else: raise ValueError("Failed to start/stop recording in Blocks in %s!" % version)
        self.validate_sound_types(output, version, default_sound_type)
        return output

    def analyze_default_sound_type(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]]) -> str:
        SOUND_TYPE_DECLARER = "    public static final "
        sound_type_class = None
        for line in file_contents:
            line = line.rstrip()
            if sound_type_class is None:
                if line.startswith(SOUND_TYPE_DECLARER) and "\"stone\"" in line:
                    sound_type_class = line.replace(SOUND_TYPE_DECLARER, "").split(" ")[0]
                    default_sound_type_declarer = "    public %s " % sound_type_class
            else:
                if line.startswith(default_sound_type_declarer):
                    default_sound_type = line.split(" ")[-1].replace(";", "")
                    if default_sound_type not in sound_types:
                        raise KeyError("Default sound type \"%s\" is not a valid sound type in Blocks in %s!" % (default_sound_type, version))
                    return default_sound_type
        else: raise ValueError("Failed to start/stop recording in Blocks.analyze_default_sound_type in %s!" % version)

    def validate_sound_types(self, blocks:dict[int,dict[str,any]], version:str, default_sound_type:str) -> None:
        REQUIRED_BLOCK_PROPERTIES = set(["code_name", "sound_type"])
        sound_type_allowances = set(self.sound_type_allowances)
        error_list:list[str] = []
        for block_id, block_properties in list(blocks.items()):
            if set(block_properties.keys()) != REQUIRED_BLOCK_PROPERTIES:
                error_list.append("Block properties \"[%s]\" for %s are not the required properties (\"[%s]\")!" % (", ".join(list(block_properties.keys())), block_id, ", ".join(list(REQUIRED_BLOCK_PROPERTIES))))
            elif block_properties["sound_type"] == None:
                if block_id not in sound_type_allowances:
                    error_list.append("Block %s has a null sound type but shouldn't be!" % block_id)
                blocks[block_id]["sound_type"] = default_sound_type # set it for when it doesn't error
            elif block_properties["sound_type"] == default_sound_type:
                if block_id not in sound_type_allowances:
                    error_list.append("Block %s has the default sound type but shouldn't be!" % block_id)
        if len(error_list) > 0:
            raise ValueError("In Blocks in %s: " % version + " ".join(error_list))

    def activate(self, version:str, store:bool=True) -> dict[int,dict[str,any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        sound_types = SoundType.SoundType.get_data_file(version)
        if sound_types == {}: raise ValueError("SoundTypes returned empty dict in Blocks in %s!" % version)
        blocks = self.analyze(blocks_file_contents, version, sound_types)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

import os

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks9(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.sound_type_allowances:list[str] = []
        if "sound_type_allowances" in kwargs:
            self.sound_type_allowances = kwargs["sound_type_allowances"]
    
    def search(self, version:str) -> str:
        '''Returns the file path of Blocks.java'''
        blocks_files = Searcher.search(version, "client", ["stone"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file
    
    def analyze_default_sound_type(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]]) -> tuple[str,str,str]:
        '''Returns the base sound type class name, the sound type variable shared by all blocks (e.g. "aq"), and the default sound type'''
        SOUND_TYPE_DECLARER = "    private static "
        sound_type_class = None
        for line in file_contents:
            line = line.rstrip()
            if sound_type_class is None and line.startswith(SOUND_TYPE_DECLARER):
                sound_type_class = line.replace(SOUND_TYPE_DECLARER, "").split(" ")[0]
                default_sound_type_declarer = "    public %s " % sound_type_class
            elif sound_type_class is not None and line.startswith(default_sound_type_declarer):
                split_line = line.replace(default_sound_type_declarer, "").split(" ")
                block_sound_type_variable = split_line[0]
                default_sound_type = split_line[-1].replace(";", "")
                if default_sound_type not in sound_types:
                    raise KeyError("Default sound type \"%s\" in line \"%s\" in Blocks in %s is not a valid sound type!" % (default_sound_type, line, version))
                return sound_type_class, block_sound_type_variable, default_sound_type
        else: raise ValueError("Unable to find default sound type due to failure to break in Blocks in %s!" % version)

    def should_skip_line(self, line:str, skip_lines:list[str]) -> bool:
        for skip_line in skip_lines:
            if line.startswith(skip_line): return True
        else: return False

    def is_block_variable_declarer(self, line:str, version:str, block_variable_declarer:str) -> bool:
        if not line.startswith(block_variable_declarer): return False
        elif line.replace(block_variable_declarer, "").split(" ")[1] != "=": return False
        else: return True

    def is_block_declarer(self, line:str, version:str, block_variable:str|None) -> bool:
        if block_variable is None: return False
        return line.startswith(f"        {block_variable} = new ")

    def is_boolean_setter(self, line:str, version:str) -> bool:
        return line.endswith(" = false;") or line.endswith(" = true;")

    def is_sound_type_variable_setter(self, line:str, version:str, sound_type_variables:dict[str,str]) -> bool:
        KEY = "        %s = "
        for sound_type_variable in sound_type_variables:
            if line.startswith(KEY % sound_type_variable): return True
        else: return False

    def is_double_sound_type_setter(self, line:str, version:str) -> bool:
        return line.count(" = ") == 2

    def is_sound_type_setter(self, line:str, version:str, block_sound_type_variable:str) -> bool:
        return f".{block_sound_type_variable} = " in line 

    def is_single_line_setter(self, line:str, version:str, block_variable) -> bool:
        if line.endswith(f" = {block_variable};"): return False
        split_line = line.lstrip().split(" ")
        code_name = split_line[0]
        if not code_name.isalpha(): return False
        elif split_line[1] != "=": return False
        else: return True

    def is_block_setter(self, line:str, version:str, block_variable:str) -> bool:
        return line.endswith(f" = {block_variable};")

    def get_block_id(self, line:str, version:str) -> int:
        if "(" not in line or ")" not in line: raise ValueError(f"Parentheses are not in line \"{line}\" in Blocks in {version}!")
        block_id = line.split("(")[1].split(")")[0].split(",")[0]
        if not block_id.isdigit(): raise ValueError(f"Apparent block id \"{block_id}\" is not a valid integer in Blocks in {version}!")
        block_id = int(block_id)
        return block_id

    def code_name_already_exists(self, line:str, version:str, blocks:dict[int,dict[str,any]], code_name:str) -> None:
        for block_name, block_properties in list(blocks.items()):
            if "code_name" not in block_properties: continue
            if block_properties["code_name"] == code_name:
                raise ValueError(f"Block with code name \"{code_name}\" already exists at {block_name} in Blocks in {version}: \"{line}\"")
        else: return None # success case

    def analyze(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], file_name:str) -> dict[int,dict[str,any]]:
        SKIP_LINES = ["        boolean bl"]
        STATIC_START = "    static {"
        RECORD_END = "    }"
        MAGIC_NUMBER = str(256)
        output:dict[int,dict[str,any]] = {}
        sound_type_class, block_sound_type_variable, default_sound_type = self.analyze_default_sound_type(file_contents, version, sound_types)
        met_static, met_magic_number, recording = False, False, False
        sound_type_variables:dict[str,str] = {} # e.g. {"g4": None|"ar"}
        SOUND_TYPE_VARIABLE_DECLARER = f"        {sound_type_class} "
        BLOCK_VARIABLE_DECLARER = f"        {file_name} "
        BLOCK_VARIABLE_SETTER = None
        block_variable = None

        for line in file_contents:
            line = line.rstrip()
            if self.should_skip_line(line, SKIP_LINES): continue
            elif line.startswith(STATIC_START):
                if met_static: raise ValueError(f"Encountered start static line multiple times in Blocks in {version}!")
                met_static = True
            elif met_static and not met_magic_number and not recording and line.startswith(SOUND_TYPE_VARIABLE_DECLARER): # section at top of static that declares sound type variables
                sound_type_variable = line.replace(SOUND_TYPE_VARIABLE_DECLARER, "").replace(";", "")
                if not sound_type_variable.startswith(sound_type_class): raise ValueError(f"Sound type variable \"{sound_type_variable}\" in line \"{line}\" does not start with \"{sound_type_class}\" in Blocks in {version}!")
                sound_type_variables[sound_type_variable] = None
            elif not met_magic_number and MAGIC_NUMBER in line: met_magic_number = True
            elif met_static and line.startswith(RECORD_END): met_static = False; break
            elif recording or met_magic_number and not recording and MAGIC_NUMBER not in line:
                recording = True
                if not line.endswith(";"): raise ValueError(f"Line \"{line}\" does not end in \";\" in Blocks in {version}!")

                elif self.is_block_variable_declarer(line, version, BLOCK_VARIABLE_DECLARER): # e.g. "m m2 = "
                    if BLOCK_VARIABLE_SETTER is not None: raise ValueError(f"Set block_variable_setter multiple times in Blocks in {version}: \"{line}\"")
                    block_variable = line.lstrip().split(" ")[1] # e.g. "m2"
                    BLOCK_VARIABLE_SETTER = f"        {block_variable} = "
                    block_id = self.get_block_id(line, version)
                    if block_id in output: raise ValueError(f"Block id {block_id} has already been recorded in Blocks in {version}: \"{line}\"")
                    output[block_id] = {}

                elif self.is_block_declarer(line, version, block_variable): # e.g. "m2 = new t(2).a(0.6f);"
                    block_id = self.get_block_id(line, version)
                    if block_id in output: raise ValueError(f"Block id {block_id} has already been recorded in Blocks in {version}: \"{line}\"")
                    output[block_id] = {}

                elif self.is_boolean_setter(line, version): continue # these are unrelated to sounds

                elif self.is_sound_type_variable_setter(line, version, sound_type_variables): # e.g. "g6 = aq;"
                    split_line = line.lstrip().split(" ")
                    sound_type_variable = split_line[0]
                    sound_type_value = split_line[-1].replace(";", "")
                    if sound_type_value not in sound_types: raise KeyError(f"Apparent sound type name \"{sound_type_value}\" is not a real sound type in Blocks in {version}: \"{line}\"")
                    if sound_type_variable not in sound_type_variables: raise KeyError(f"Sound type variable \"{sound_type_variable}\" is not a real sound type variable in Blocks in {version}: {line}")
                    sound_type_variables[sound_type_variable] = sound_type_value

                elif self.is_double_sound_type_setter(line, version): # e.g. "v0.ao = g6 = ar;"
                    split_line = line.lstrip().split(" ")
                    sound_type_variable = split_line[2]
                    sound_type_value = split_line[4].replace(";", "")
                    if sound_type_value not in sound_types: raise KeyError(f"Apparent sound type name \"{sound_type_value}\" is not a real sound type in Blocks in {version}: \"{line}\"")
                    if sound_type_variable not in sound_type_variables: raise KeyError(f"Sound type variable \"{sound_type_variable}\" is not a real sound type variable in Blocks in {version}: {line}")
                    sound_type_variables[sound_type_variable] = sound_type_value
                    sound_type = sound_type_value
                
                elif self.is_sound_type_setter(line, version, block_sound_type_variable): # e.g. ".ao = g6;"
                    sound_type_variable = line.split(" ")[-1].replace(";", "")
                    if sound_type_variable not in sound_type_variables: raise KeyError(f"Sound type variable \"{sound_type_variable}\" is not a real sound type variable in Blocks in {version}: {line}")
                    sound_type = sound_type_variables[sound_type_variable]

                elif self.is_single_line_setter(line, version, block_variable): # e.g. "p = new i(..."
                    split_line = line.lstrip().split(" ")
                    sound_type = None
                    code_name = split_line[0]
                    self.code_name_already_exists(line, version, output, code_name)
                    block_id = self.get_block_id(line, version)
                    if block_id in output: raise ValueError(f"Block id {block_id} has already been recorded in Blocks in {version}: \"{line}\"")
                    output[block_id] = {"sound_type": sound_type, "code_name": code_name}
                
                elif self.is_block_setter(line, version, block_variable): # e.g. "aa = m2;"
                    code_name = line.lstrip().split(" ")[0]
                    output[block_id] = {"sound_type": sound_type, "code_name": code_name}

        else: raise ValueError(f"Failed to start/stop recording in Blocks in {version}!")
        output = self.set_null_code_names(output, version)
        self.validate_sound_types(output, version, default_sound_type)
        return output

    def set_null_code_names(self, blocks:dict[int,dict[str,any]], version:str) -> dict[int,dict[str,any]]:
        for block_id, block_properties in list(blocks.items()):
            if "code_name" not in block_properties:
                blocks[block_id]["code_name"] = None
            else: continue
        return blocks

    def validate_sound_types(self, blocks:dict[int,dict[str,any]], version:str, default_sound_type:str) -> None:
        REQUIRED_BLOCK_PROPERTIES = set(["code_name", "sound_type"])
        sound_type_allowances = set(self.sound_type_allowances)
        error_list:list[str] = []
        if None in blocks: error_list.append("A block with the id of None exists!")
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
        blocks_file_name = blocks_file.split("/")[-1].split(".")[0] # get rid of path and .java
        blocks = self.analyze(blocks_file_contents, version, sound_types, blocks_file_name)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

import os

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks8(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.sound_type_allowances:list[str] = []
        if "sound_type_allowances" in kwargs:
            self.sound_type_allowances = kwargs["sound_type_allowances"]
    def search(self, version:str) -> str:
        '''Returns the file path of Blocks.java (e.g. gk.java)'''
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

    def get_sound_type(self, line:str, version:str, sound_types:dict[str,dict[str,int|str]]) -> str:
        '''Returns "au" from a line like "cn2 = au;"'''
        sound_type = line.split(" ")[-1].replace(";", "")
        if sound_type not in sound_types:
            raise ValueError("Sound type \"%s\" in line \"%s\" in Blocks in %s is not a valid sound type!" % (sound_type, line, version))
        else: return sound_type

    def get_id(self, line:str, version:str, needs_equals_new:bool=True) -> int:
        '''Returns the block's numerical id from the line'''
        if needs_equals_new:
            if " = new " not in line: raise ValueError("Attempted to get block id from line \"%s\" in Blocks in %s, but it had no \" = new\"!" % (line, version))
            block_id = line.split(" = new ")[1]
        else: block_id = line
        block_id = block_id.split("(")[1].split(")")[0].split(",")[0]
        if not block_id.isdigit(): raise ValueError("Block id \"%s\" is not an integer!" % block_id)
        else: return int(block_id)

    def get_code_name(self, line:str, version:str, block_assigner:str, block_id:int) -> str:
        '''Returns the block's code name (e.g. "l") from the line'''
        block_code_name = line.lstrip().split(" ")[0]
        if not block_code_name.isalpha(): raise ValueError("Block %s's code name \"%s\" in line \"%s\" is not alphabetical in Blocks in %s!" % (block_id, block_code_name, line, version))
        return block_code_name

    def get_code_name_from_single_line_block_declarer(self, line:str, version:str, block_variable:str, block_id:int) -> str:
        block_code_name = line.lstrip().split(" ")[0]
        if not block_code_name.isalpha(): raise ValueError("Block %s's code name \"%s\" in line \"%s\" is not alphabetical in Blocks in %s!" % (block_id, block_code_name, line, version))
        return block_code_name

    def is_single_line_block_declarer(self, line:str, version:str, block_variable_setter:str) -> bool:
        if block_variable_setter is None: return False
        if line.startswith(block_variable_setter): return False
        if " = new " in line: return True
        else: return False

    def is_sound_type_variable_declarer(self, line:str, version:str, sound_type_variable_declarer:str) -> bool:
        if not line.startswith(sound_type_variable_declarer): return False
        elif line.lstrip().split(" ")[1] == "=": return False
        else: return True

    def is_block_variable_declarer(self, line:str, version:str, block_variable_declarer:str) -> bool:
        if not line.startswith(block_variable_declarer): return False
        elif line.lstrip().split(" ")[1] == "=": return False
        else: return True

    def code_name_already_exists(self, code_name:str, blocks:dict[int,dict[str,any]]) -> bool:
        for block_properties in list(blocks.values()):
            if "code_name" in block_properties:
                if block_properties["code_name"] == code_name: return True
            else: continue
        else: return False

    def is_making_copy(self, line:str, version:str, blocks:dict[int,dict[str,any]]) -> tuple[bool,int|None]:
        '''Returns a boolean and the block id'''
        if not " = new " in line: return False, None
        block_code_name = line.split(" = new ")[1].split("(")[1].split(")")[0].split(", ")[1]
        if not block_code_name.isalpha(): return False, None
        for block_id, block_properties in list(blocks.items()):
            if "code_name" in block_properties:
                if block_properties["code_name"] == block_code_name: return True, block_id
            else: continue
        else: return False, None

    def analyze(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], file_name:str) -> dict[int,dict[str,any]]:
        def get_block_assigner(line:str, block_assigners:list[str]) -> tuple[bool,str|None]:
            '''Returns a boolean and the block assigner that it ends with'''
            for block_assigner in block_assigners:
                if block_assigner in line: return True, block_assigner
            else: return False, None
        RECORD_START = "    static {"
        RECORD_END = "        for ("
        sound_type_class, block_sound_type_variable, default_sound_type = self.analyze_default_sound_type(file_contents, version, sound_types)
        SOUND_TYPE_VARIABLE_DECLARER = "        %s " % sound_type_class
        BLOCK_VARIABLE_DECLARER = "        %s " % file_name
        SOUND_TYPE_VARIABLE_SETTER = None
        BLOCK_VARIABLE_SETTER = None
        SOUND_TYPE_ASSIGNER_START = "        new "
        block_id = None
        SOUND_TYPE_ASSIGNER = None
        BLOCK_ASSIGNERS = None
        recording = False
        sound_type_variable = None
        output:dict[int,dict[str,any]] = {}
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(RECORD_START): # START RECORDING
                if recording: raise ValueError("Recording line encountered multiple times in Blocks in %s!" % version)
                recording = True
            elif recording and " = " not in line: recording = False; break # STOP RECORDING
            elif recording:
                if line.startswith(RECORD_END): recording = False; break
                elif not line.endswith(";"): raise ValueError("Line \"%s\" in Blocks in %s does not end in \";\"" % (line, version))
                elif self.is_sound_type_variable_declarer(line, version, SOUND_TYPE_VARIABLE_DECLARER):
                    if sound_type_variable is not None: raise ValueError("Sound type variable (\"%s\") was declared multiple times in Blocks in %s: \"%s\"" % (sound_type_variable, version, line))
                    sound_type_variable = line.replace(SOUND_TYPE_VARIABLE_DECLARER, "").split(" ")[0]
                    sound_type = self.get_sound_type(line, version, sound_types)
                    SOUND_TYPE_VARIABLE_SETTER = "        %s = " % sound_type_variable
                    SOUND_TYPE_ASSIGNER = ".%s = %s;" % (block_sound_type_variable, sound_type_variable)
                elif self.is_block_variable_declarer(line, version, BLOCK_VARIABLE_DECLARER):
                    block_variable = line.replace(BLOCK_VARIABLE_DECLARER, "").split(" ")[0]
                    block_id = self.get_id(line, version, True)
                    BLOCK_VARIABLE_SETTER = "        %s = " % block_variable
                    BLOCK_ASSIGNERS = [block_assigner % block_variable for block_assigner in [" = %s;", " = %s.", ")%s;", ")%s."]]
                    if block_id in output: raise KeyError("Block %s already exists in Blocks in %s!" % (block_id, version))
                    output[block_id] = {}
                elif SOUND_TYPE_VARIABLE_SETTER is not None and line.startswith(SOUND_TYPE_VARIABLE_SETTER): # SOUND TYPE
                    sound_type = self.get_sound_type(line, version, sound_types)
                elif BLOCK_VARIABLE_SETTER is not None and line.startswith(BLOCK_VARIABLE_SETTER): # BLOCK ID
                    block_id = self.get_id(line, version, False)
                    if block_id in output: raise KeyError("Block %s already exists in Blocks in %s!" % (block_id, version))
                    output[block_id] = {}
                elif SOUND_TYPE_ASSIGNER is not None and line.endswith(SOUND_TYPE_ASSIGNER) and line.startswith(SOUND_TYPE_ASSIGNER_START):
                    block_sound_type_assigner_id = self.get_id(line, version, False)
                    if block_sound_type_assigner_id not in output: raise KeyError("Block %s does not exist while trying to set sound type in Blocks in %s!" % (block_sound_type_assigner_id, version))
                    if "sound_type" in output[block_id]: raise KeyError("Block %s's sound type already exists in Blocks in %s!" % (block_id, version))
                    output[block_id]["sound_type"] = sound_type
                elif BLOCK_ASSIGNERS is not None and get_block_assigner(line, BLOCK_ASSIGNERS)[0] and line.startswith("        "): # 
                    block_assigner = get_block_assigner(line, BLOCK_ASSIGNERS)[1]
                    block_code_name = self.get_code_name(line, version, block_assigner, block_id)
                    if "code_name" in output[block_id]: raise KeyError("Block %s's code name already exists in Blocks in %s!" % (block_id, version))
                    if self.code_name_already_exists(block_code_name, output): raise ValueError("Block code name \"%s\" already exists in Blocks in %s!" % (block_code_name, version))
                    output[block_id]["code_name"] = block_code_name
                elif self.is_single_line_block_declarer(line, version, BLOCK_VARIABLE_SETTER): # SINGLE-LINE
                    block_id = self.get_id(line, version, True)
                    block_code_name = self.get_code_name_from_single_line_block_declarer(line, version, block_variable, block_id)
                    if self.code_name_already_exists(block_code_name, output): raise ValueError("Block code name \"%s\" already exists in Blocks in %s!" % (block_code_name, version))
                    making_copy, copy_id = self.is_making_copy(line, version, output)
                    if making_copy: sound_type = output[copy_id]["sound_type"]
                    else: sound_type = None
                    if block_id in output: raise KeyError("Block %s already exists in Blocks in %s!" % (block_id, version))
                    output[block_id] = {"sound_type": sound_type, "code_name": block_code_name}
                else: raise ValueError("Line \"%s\" is wonky in Blocks in %s!" % (line, version))
        else: raise ValueError("Failed to start/stop recording in Blocks in %s!" % version)
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

import os

import DataMiners.DataMiner as DataMiner
import DataMiners.SoundType.SoundType as SoundType
import Utilities.Searcher as Searcher

class Blocks5(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.sound_type_allowances:list[str] = []
        if "sound_type_allowances" in kwargs:
            self.sound_type_allowances = kwargs["sound_type_allowances"]

    def search(self, version:str) -> str:
        '''Returns the file path of Blocks.java (e.g. aqz.java)'''
        blocks_files = Searcher.search(version, "client", ["stone", "grass", "leaves", "dispenser"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def try_to_find_new_and_old_name_functions(self, line:str, version:str) -> tuple[str|None,str|None]:
        '''If conditions are met, it will return the old name function and the new name function'''
        def get_function(item:str, line:str) -> str:
            quoted_item = "\"%s\"" % item
            if quoted_item not in line: raise ValueError("Item \"%s\" is not in line \"%s\" in Blocks in %s!" % (item, line, version))
            return line.split("(%s)" % quoted_item)[0].split(".")[-1]
        OLD_SIGNIFIERS = ["stonebrick", "oreGold", "oreIron", "oreCoal", "oreLapis", "blockLapis"]
        quote_count = line.count("\"")
        if quote_count % 2 == 1:
            raise ValueError("Number of quotes (%s) in line \"%s\" is an odd number in Blocks in %s!" % (quote_count, line, version))
        elif quote_count == 0: return None, None
        elif quote_count == 2: return None, None
        elif quote_count > 4:
            raise ValueError("Number of quotes (%s) in line \"%s\" is above 4 in Blocks in %s!" % (quote_count, line, version))
        elif quote_count == 4:
            if quote_count > 4: quote_offset = quote_count - 4
            else: quote_offset = 0
            split_line = line.split("\"")
            item1, item2 = split_line[1 + quote_offset], split_line[3 + quote_offset]
            if item1 == item2: return None, None
            yippee_it_found_something = False
            if item1 in OLD_SIGNIFIERS:
                old_function, new_function = get_function(item1, line), get_function(item2, line)
                yippee_it_found_something = True
            elif item2 in OLD_SIGNIFIERS:
                old_function, new_function = get_function(item2, line), get_function(item1, line)
                yippee_it_found_something = True
            if yippee_it_found_something:
                if old_function == new_function: raise ValueError("Old function \"%s\" and new function \"%s\" are for some reason equal to each other in Blocks in %s!" % (old_function, new_function, version))
                return old_function, new_function
        return None, None

    def analyze_old_and_new_functions(self, file_contents:list[str], version:str, file_name:str) -> tuple[str,str]:
        for line in file_contents:
            line = line.rstrip()
            thing = self.try_to_find_new_and_old_name_functions(line, version)
            old_function, new_function = thing
            if old_function is not None and new_function is not None:
                return old_function, new_function
        else: raise ValueError("Unable to find old name function and new name function before end of file in Blocks in %s!" % version)

    def get_sound_type(self, line:str, sound_types:dict[str,dict[str,int|str]], version:str, keys:list[str]=None, backup:str|None=None) -> str|None:
        '''Attempts to return the sound type of the line, and returns the backup (or None) if it can't'''
        def get_replacement(key:str, sound_type_name:str) -> str:
            if key.count("%s") == 1:
                return key % sound_type_name
            else: raise ValueError("Unsupported number of \"%s\"s in key \"%s\" in Blocks in %s!" % ("%s", key, version))
        if keys is None: keys = [".a(%s)"] # I am assuming the function is called "a" since there shouldn't be many functions acting on just a sound type
        strings_to_test_for:dict[str,list[str]] = {}
        for sound_type in sound_types:
            strings_to_test_for[sound_type] = [get_replacement(key, sound_type) for key in keys]
        for sound_type, test_strings in list(strings_to_test_for.items()):
            for test_string in test_strings:
                if test_string in line: return sound_type
                else: continue
        else: return backup

    def get_numeric_id(self, line:str, version:str) -> int:
        output = ""
        for character in line:
            if character.isdigit():
                output += character
            else:
                if output == "": continue
                else: return int(output)
        else: raise ValueError("Line \"%s\"'s does not have a numeric id in Blocks in %s!" % (line, version))

    def get_name_from_function(self, line:str, function_name:str) -> str|None:
        '''Returns a block name (e.g. \"stone\") using the name declaring function (e.g. \"e\") or None if it does not exist.'''
        big_string = ".%s(\"" % function_name
        if big_string not in line: return None
        else: return line.split(big_string)[1].split("\")")[0]

    def get_template(self, line:str, blocks:dict[str,dict[str,any]], version:str) -> tuple[bool,dict[str,any]|None]:
        '''Sees if it can get any properties based off of template, and returns that boolean of if it did and the template data.'''
        parameters = line.split("new ")[1].split("(")[1].split(")")[0].split(", ")
        if len(parameters) == 0: return False, None # raise ValueError("Line \"%s\" in Blocks in %s has no parameters!" % (line, version))
        elif len(parameters) == 1: return False, None # raise ValueError("Line \"%s\" in Blocks in %s does not have enough parameters!" % (line, version))
        block_parameter = parameters[1]
        if block_parameter in blocks: return True, blocks[block_parameter]
        else: return False, None

    def analyze_default_sound_type(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]]) -> str:
        SOUND_TYPE_DECLARER = "    public static final "
        DEFAULT_SOUND_TYPE_DECLARER = None
        sound_type_class = None
        for line in file_contents:
            line = line.rstrip()
            if sound_type_class is None:
                if line.startswith(SOUND_TYPE_DECLARER):
                    sound_type_class = line.replace(SOUND_TYPE_DECLARER, "").split(" ")[0]
                    DEFAULT_SOUND_TYPE_DECLARER = "    public %s " % sound_type_class
            elif DEFAULT_SOUND_TYPE_DECLARER is not None and line.startswith(DEFAULT_SOUND_TYPE_DECLARER):
                default_sound_type = line.split(" = ")[1].replace(";", "")
                break
        else: raise ValueError("Did not find default sound type before end of file in Blocks in %s!" % version)
        if default_sound_type not in sound_types:
            raise ValueError("Got wonky sound type \"%s\", which is not a sound type in Blocks in %s!" % (default_sound_type, version))
        return default_sound_type

    def analyze(self, file_contents:list[str], version:str, sound_types:dict[str,dict[str,int|str]], file_name:str) -> dict[int,dict[str,any]]:
        RECORD_START = "    public static final "
        MAGIC_NUMBER = str(4096)
        old_name_function, new_name_function = self.analyze_old_and_new_functions(file_contents, version, file_name)
        met_magic_number = False
        recording = False
        subclasses = self.analyze_block_subclasses_to_analyze(file_contents, version, file_name)
        subclass_properties:dict[str,dict[str,any]] = {}
        self.analyze_subclasses(subclasses, version, subclass_properties, file_name, sound_types)
        output:dict[int,dict[str,any]] = {}
        default_sound_type = self.analyze_default_sound_type(file_contents, version, sound_types)
        for line in file_contents:
            line = line.rstrip()
            if MAGIC_NUMBER in line: met_magic_number = True
            elif line.startswith(RECORD_START) and met_magic_number:
                recording = True
            elif len(output) > 0: break # it ends at the first weird line
            if recording:
                code_name = line.replace(RECORD_START, "").split(" ")[1]
                numeric_id = self.get_numeric_id(line, version)
                old_name = self.get_name_from_function(line, old_name_function)
                new_name = self.get_name_from_function(line, new_name_function)
                block_subclass = line.split("new ")[1].split("(")[0]
                sound_type = self.get_sound_type(line, sound_types, version, backup=subclass_properties[block_subclass]["sound_type"])
                is_template, template_data = self.get_template(line, output, version)
                if is_template:
                    if old_name is None: old_name = template_data["old_name"]
                    if new_name is None: new_name = template_data["new_name"]
                    if sound_type is None: sound_type = template_data["sound_type"]
                output[code_name] = {"id": numeric_id, "new_name": new_name, "old_name": old_name, "sound_type": sound_type}
        else: raise ValueError("Blocks in %s did not start/stop recording before end of file!" % version)
        self.validate_sound_types(output, version, default_sound_type)
        return output

    def validate_sound_types(self, blocks:dict[str,dict[str,any]], version:str, default_sound_type:str) -> None:
        def is_in_allowances(numeric_id:int, new_name:str) -> bool:
            if numeric_id in sound_type_allowances: return True
            elif new_name in sound_type_allowances: return True
            else: return False
        def get_best_identifier(block_properties:dict[str,any]) -> str|int:
            return block_properties["new_name"] if block_properties["new_name"] is not None else block_properties["id"]
        REQUIRED_BLOCK_PROPERTIES = set(["id", "old_name", "new_name", "sound_type"])
        sound_type_allowances = set(self.sound_type_allowances)
        error_list:list[str] = []
        for block_code_name, block_properties in list(blocks.items()):
            if set(block_properties.keys()) != REQUIRED_BLOCK_PROPERTIES:
                best_identifier = get_best_identifier(block_properties)
                error_list.append("Block properties \"[%s]\" for %s are not the required properties (\"[%s]\")!" % (", ".join(list(block_properties.keys())), best_identifier, ", ".join(list(REQUIRED_BLOCK_PROPERTIES))))
            elif block_properties["sound_type"] == None:
                if not is_in_allowances(block_properties["id"], block_properties["new_name"]):
                    print(block_properties["new_name"], block_properties["new_name"] in sound_type_allowances, block_properties["id"], block_properties["id"] in sound_type_allowances)
                    best_identifier = get_best_identifier(block_properties)
                    error_list.append("Block \"%s\" has a null sound type but shouldn't be!" % best_identifier)
                blocks[block_code_name]["sound_type"] = default_sound_type # set it for when it doesn't error
            elif block_properties["sound_type"] == default_sound_type:
                if not is_in_allowances(block_properties["id"], block_properties["new_name"]):
                    best_identifier = get_best_identifier(block_properties)
                    error_list.append("Block \"%s\" has the default sound type but shouldn't be!" % best_identifier)
        if len(error_list) > 0:
            raise ValueError("In Blocks in %s: " % version + " ".join(error_list))

    def open_file(self, file_name:str, version:str) -> list[str]:
        with open(os.path.join("./_versions", version, "client_decompiled", file_name + ".java"), "rt") as f:
            return f.readlines()

    def analyze_subclasses(self, files:list[str], version:str, properties:dict[str,dict[str,any]], default_file_name:str, sound_types:dict[str,dict[str,int|str]]) -> None:
        for file_name in files:
            if file_name in properties: continue
            file_contents = self.open_file(file_name, version)
            self.analyze_subclass(file_contents, file_name, version, properties, default_file_name, sound_types)
        properties = DataMiner.DataMiner.sort_dict(properties)

    def analyze_subclass(self, file_contents:list[str], file_name:str, version:str, properties:dict[str,dict[str,any]], default_file_name:str, sound_types:dict[str,dict[str,int|str]]) -> None:
        # NOTE: This does not make an attempt to get names, old or new
        def should_start_recording(line:str) -> bool:
            for start_recording in START_RECORDINGS:
                if line.startswith(start_recording % file_name): return True
            else: return False
        START_RECORDINGS = ["    protected %s(", "    public %s("]
        STOP_RECORDING = "    }"
        EXTENSION_DECLARATION = "extends "
        recording = False
        if file_name in properties: raise ValueError("Repeated \"%s\" subclass in Blocks in %s!" % (file_name, version))
        properties[file_name] = {"sound_type": None}
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(EXTENSION_DECLARATION):
                superclass = line.replace(EXTENSION_DECLARATION, "").split(" ")[0]
                if superclass == default_file_name: continue
                if superclass not in properties:
                    superclass_file_contents = self.open_file(superclass, version)
                    self.analyze_subclass(superclass_file_contents, superclass, version, properties, default_file_name, sound_types)
                properties[file_name] = properties[superclass]
                assert properties[file_name] == properties[superclass]
            elif should_start_recording(line):
                if recording: raise ValueError("Start recording line occured twice in Blocks.analyze_subclass in subclass \"%s\" in %s!" % (file_name, version))
                recording = True
            elif line.startswith(STOP_RECORDING): recording = False; break
            elif recording:
                if properties[file_name]["sound_type"] is None: properties[file_name]["sound_type"] = self.get_sound_type(line, sound_types, version, keys=["this.a(%s)"])
        else: raise ValueError("Blocks.analyze_subclass in subclass \"%s\" in %s did not start/stop before reaching end of file!" % (file_name, version))

    def analyze_block_subclasses_to_analyze(self, file_contents:list[str], version:str, file_name:str) -> list[str]:
        RECORD_START = "    public static final "
        MAGIC_NUMBER = str(4096)
        met_magic_number = False
        recording = False
        output:list[str] = []
        for line in file_contents:
            line = line.rstrip()
            if MAGIC_NUMBER in line: met_magic_number = True
            elif line.startswith(RECORD_START) and met_magic_number:
                recording = True
            elif len(output) > 0: break
            if recording:
                block_subclass = line.split("new ")[1].split("(")[0]
                output.append(block_subclass)
        else: raise ValueError("Blocks.analyze_block_subclasses_to_analyze in %s did not start/stop recording before end of file!" % version)
        return sorted(output)

    def activate(self, version:str, store:bool=True) -> dict[int,dict[str,any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        sound_types = SoundType.SoundType.get_data_file(version)
        if sound_types == {}: raise ValueError("SoundTypes returned empty dict in Blocks in %s!" % version)
        blocks_file_name = blocks_file.split(".")[0] # without ".java"
        blocks = self.analyze(blocks_file_contents, version, sound_types, blocks_file_name)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

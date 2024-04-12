import os
from typing import Any

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

class Blocks0(DataMiner.DataMiner):
    IMPORT_START = ""
    IMPORT_END = ""
    BLOCKS_START = "public class Blocks {"
    FUNCTION_START = ""

    START_TYPE = None
    IMPORT_TYPE  = "import"
    IMPORT_END_TYPE = "import end"
    BLOCKS_TYPE = "blocks"
    FUNCTION_TYPE = "function"
    WOOD_WOOD_TYPE = "wood"
    HANGING_SIGN_WOOD_TYPE = "hanging_sign"

    BLOCK_FUNCTION_START = "    private static "
    BLOCK_FUNCTION_END = "    }"
    SOUND_INDICATOR = "SoundType."
    COPY_INDICATOR = ".copy("
    WOODTYPE_INDICATOR = "WoodType."
    BLOCKSETTYPE_INDICATOR = "BlockSetType."
    BLOCK_LINE = "    public static final Block "
    
    MODULE_SOUND_TYPE_START = "    public SoundType getSoundType"
    MODULE_SOUND_TYPE_END = "    }"

    WOODTYPE_INDEXES = {WOOD_WOOD_TYPE: 0, HANGING_SIGN_WOOD_TYPE: 1}

    def search(self, version:str) -> str:
        '''Returns the file path of the desired file.'''
        blocks_files = Searcher.search(version, "client", ["only:file:Blocks.java", "not:path:references"], ["and"], allow_decompile=True)
        if len(blocks_files) > 1:
            print("\n".join(blocks_files))
            raise FileExistsError("Too many Blocks files found for %s" % version)
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file
    
    def search_woodtype(self, version:str) -> str:
        '''Returns the path of the WoodType file.'''
        woodtype_files = Searcher.search(version, "client", ["only:file:WoodType.java"], suppress_clear=True, allow_decompile=True)
        if len(woodtype_files) > 1:
            print("\n".join(woodtype_files))
            raise FileExistsError("Too many WoodType files found for %s" % version)
        elif len(woodtype_files) == 0:
            raise FileNotFoundError("No WoodType file found for %s" % version)
        else: woodtype_file = woodtype_files[0]
        return woodtype_file

    def search_blocksettype(self, version:str) -> str:
        '''Returns the path of the BlockSetType file.'''
        blocksettype_files = Searcher.search(version, "client", ["only:file:BlockSetType.java"], suppress_clear=True, allow_decompile=True)
        if len(blocksettype_files) > 1:
            print("\n".join(blocksettype_files))
            raise FileExistsError("Too many BlockSetType files found for %s" % version)
        elif len(blocksettype_files) == 0:
            raise FileNotFoundError("No BlockSetType file found for %s" % version)
        else: blocksettype_file = blocksettype_files[0]
        return blocksettype_file

    def get_recording(self, line:str, current:str) -> tuple[str, bool]:
        '''Returns what should be recorded based on the line'''
        if line == self.IMPORT_START   and current == self.START_TYPE:  return self.IMPORT_TYPE,     True
        if line == self.IMPORT_END     and current == self.IMPORT_TYPE: return self.IMPORT_END_TYPE, True
        if line == self.BLOCKS_START   and current == self.IMPORT_END_TYPE: return self.BLOCKS_TYPE,     True
        if line == self.FUNCTION_START and current == self.BLOCKS_TYPE: return self.FUNCTION_TYPE,   True
        return current, False

    def get_import(self, line:str, line_index:int, version:str) -> str:
        '''Returns the module from the line; checks that the file exists.'''
        LINE_START = "import "
        LINE_END = ";"
        IGNORE_FILES = {
            "com.google.common.collect.ImmutableList",
            "java.util.Map",
            "java.util.function.Consumer",
            "java.util.function.Function",
            "java.util.function.Predicate",
            "java.util.function.Supplier",
            "java.util.function.ToIntFunction",
            "javax.annotation.Nullable",
            }
        if not line.startswith(LINE_START):
            raise ValueError("Importer line %s (\"%s\") does not start with \"%s\"!" % (line_index, line, LINE_START))
        if not line.endswith(LINE_END): raise ValueError("Importer line %s (\"%s\") does not end with \"%s\"!" % (line_index, line, LINE_END))
        module = line.replace(LINE_START, "").replace(LINE_END, "")
        if module not in IGNORE_FILES:
            path = module.replace(".", "/")
            if not os.path.exists("./_versions/%s/client_decompiled/%s.java" % (version, path)):
                raise FileNotFoundError("Unable to import file \"%s\" (line %s)" % (module, line_index))
        return module

    def get_function_name(self, line:str, line_index:int) -> str:
        '''Returns the function name from a function in the function section.'''
        VALID_START_CHARACTERS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
        VALID_CHARACTERS = VALID_START_CHARACTERS + "1234567890_"
        if not line.startswith(self.BLOCK_FUNCTION_START):
            raise ValueError("Function line %s (\"%s\") does not start with \"%s\"!" % (line_index, line, self.BLOCK_FUNCTION_START))
        function_name = line.replace(self.BLOCK_FUNCTION_START, "").split(" ")[1].split("(")[0]

        # Error messages are important
        if function_name[0] not in VALID_START_CHARACTERS:
            raise ValueError("Function name \"%s\" in line %s (\"%s\") does not start with a valid character!" % (function_name, line_index, line))
        for character in function_name:
            if character not in VALID_CHARACTERS:
                raise ValueError("Function name \"%s\" in line %s (\"%s\") contains invalid characters!" % (function_name, line_index, line))
        return function_name

    def get_import_from_module(self, importers:list[str], module_name:str) -> str:
        '''Returns the full path of an import from the shortened name'''
        for importer in importers:
            importer_short = importer.split(".")[-1]
            if importer_short == module_name: return importer
        else: raise KeyError("Module \"%s\" does not exist in imports!" % module_name)

    def get_block_function(self, line:str, line_index:int) -> tuple[str|None, bool]:
        '''If this line contains a special block-creating function, returns the function name and True, else returns None and False'''
        def function_error(text:str) -> None:
            raise ValueError("Block function line %s (\"%s\")'s function (\"%s\") %s!" % (line_index, line, block_function, text))
        LINE_START = "    public static final Block "
        if not line.startswith(LINE_START):
            raise ValueError("Block function line %s (\"%s\") does not start with \"%s\"!" % (line_index, line, LINE_START))
        is_normal = line.split("\"")[2].split(" ")[1] == "new"
        if is_normal: return (None, False)
        block_function = line.split(", ")[1].split("(")[0]
        if block_function.count(".") > 1: function_error("has too many \".\"s")
        if block_function.count(".") == 0: function_error("doesn't have any \".\"")
        if block_function.split(".")[0] != "Blocks": function_error("is not under file \"Blocks\"")
        block_function = block_function.split(".")[1]
        return block_function, True

    def get_module(self, line:str, line_index:int, function_module:list[str]|None=None, is_function:bool=False) -> tuple[str|None, bool]:
        '''Returns the module name and True if it exists, else returns None and False'''
        splitters = {False: "\", new ", True: "return new "}
        splitter = splitters[is_function]
        if splitter in line:
            module_name = line.split(splitter)[1].split("(")[0]
            return module_name, True
        elif function_module is not None:
            function_name, is_function = self.get_block_function(line, line_index)
            if is_function:
                module_name = function_module[function_name]
                return module_name, True
        return None, False

    def get_import_modules(self, imports:list[str]) -> dict[str,str]:
        '''Returns a dict with shortened names as keys and full names as values'''
        output = {}
        for importer in imports:
            short_name = importer.split(".")[-1]
            output[short_name] = importer
        return output

    def get_sound_type_from_module(self, file_data:str) -> list[str]:
        '''Returns a list of sound types based on the file'''
        lines = file_data.split("\n")
        output:list[str] = []
        recording = False
        for line in lines:
            line = line.replace("\n", "")
            if line.startswith(self.MODULE_SOUND_TYPE_START):
                recording = True
                continue
            if line.startswith(self.MODULE_SOUND_TYPE_END) and recording:
                recording = False
                break
            if recording:
                if self.SOUND_INDICATOR in line:
                    sound_type = line.split(self.SOUND_INDICATOR)[1].split(";")[0]
                    output.append(sound_type)
        return output

    def analyze_woodtype(self, version:str) -> dict[str,list[str]]:
        '''Analyzes the WoodType.java file, and returns a dict of woodtypes and dict of wood/hanging_sign and sound type'''
        WOODTYPE_START = "    public static final WoodType "
        WOODTYPE_END = "    }"
        woodtype_file = self.search_woodtype(version)
        with open(os.path.join("./_versions", version, "client_decompiled", woodtype_file), "rt") as f:
            lines = f.readlines()
        
        defaults = []
        recording = False
        for line in lines:
            line = line.replace("\n", "")
            # FIRST PASS; gather defaults
            if line.startswith("    public WoodType(String string, BlockSetType blockSetType) {"):
                recording = True
                continue
            if line.startswith(WOODTYPE_END) and recording: break
            if recording:
                stripped_line = line.replace("        this(", "").replace(");", "")
                parameters = stripped_line.split(", ")
                for parameter in parameters:
                    if "SoundType." in parameter:
                        defaults.append(parameter.replace("SoundType.", ""))
        
        output:dict[str,] = {}
        for line in lines:
            # SECOND PASS; analyze woodtypes
            line = line.replace("\n", "")
            if not line.startswith(WOODTYPE_START): continue
            code_name = line.replace(WOODTYPE_START, "").split(" ")[0]
            parameters = line.split("(")[2].split(")")[0].split(", ")
            sound_types = [parameter.split(".")[1] for parameter in parameters if parameter.startswith("SoundType.")]
            while len(sound_types) < len(defaults):
                sound_types.append(defaults[len(sound_types)])
            output[code_name] = sound_types
        return output

    def analyze_blocksettype(self, version:str) -> dict[str,str]:
        '''Analyzes the BlockSetType.java file, and returns a dict of block set types and their sound types.'''
        BLOCKSETTYPE_START = "    public BlockSetType(String string) {"
        BLOCKSETTYPE_END = "    }"
        BLOCKSETTYPE_INDICATOR = "    public static final BlockSetType "
        blocksettype_file = self.search_blocksettype(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocksettype_file), "rt") as f:
            lines = f.readlines()
        
        recording = False
        for line in lines:
            # FIRST PASS; gather default
            if line.startswith(BLOCKSETTYPE_START):
                recording = True
                continue
            if line.startswith(BLOCKSETTYPE_END): break
            if recording:
                stripped_line = line.replace("        this(", "").replace(");", "")
                parameters = stripped_line.split(", ")
                default = [parameter.split(".")[1] for parameter in parameters if parameter.startswith("SoundType.")][0]
        
        output:dict[str,str] = {}
        for line in lines:
            # SECOND PASS; analyze blocksettypes
            code_name = line.replace(BLOCKSETTYPE_INDICATOR, "").split(" ")[0]
            if line.startswith(BLOCKSETTYPE_INDICATOR):
                if "SoundType." not in line: output[code_name] = default
                else:
                    sound_type = line.split("SoundType.")[1].split(")")[0].split(",")[0]
                    output[code_name] = sound_type
        return output

    def get_copy(self, blocks:dict[str,dict[str,Any]], code_to_block:dict[str,str], line:str, line_index:int) -> tuple[str|None, bool]:
        '''Returns the sound type of the copied thing'''
        def no_exist_error() -> None:
            raise KeyError("Block line %s (\"%s\") references a block (\"%s\") that does not exist!" % line_index, line, copy_block_code)
        copy_block_code = line.split(self.COPY_INDICATOR)[1].split(")")[0]
        if copy_block_code not in code_to_block: no_exist_error()
        copy_block = code_to_block[copy_block_code]
        if copy_block not in blocks: no_exist_error()
        if "sound_type" in blocks[copy_block]:
            return blocks[copy_block]["sound_type"], True
        else: return None, False

    def analyze(self, file_contents:list[str], version:str) -> dict[str,dict[str,Any]]:
        recording = self.START_TYPE
        function_recording = False
        imports:list[str] = []
        blocks_lines:list[str] = [] # stores lines of blocks section for later
        block_functions:set[str] = set() # names of functions that create blocks
        line_starts:dict[str,int] = {} # keeps track of when sections start
        function_sounds:dict[str,str] = {} # matches function names to sound types.
        function_module:dict[str,str] = {} # matches functions to the block module they use
        
        for line_index, line in enumerate(file_contents):
            # FIRST PASS, collect imports and functions
            line = line.replace("\n", "").replace("(Block)", "")
            recording, skip = self.get_recording(line, recording)
            if skip: line_starts[recording] = line_index + 1; continue
            if recording == self.IMPORT_TYPE:
                imports.append(self.get_import(line, line_index, version))
            if recording == self.BLOCKS_TYPE:
                blocks_lines.append(line)
                block_function, use = self.get_block_function(line, line_index)
                if use: block_functions.add(block_function)
            if recording == self.FUNCTION_TYPE:
                if line.startswith(self.BLOCK_FUNCTION_START):
                    if function_recording: raise ValueError("Function was nested at line %s (\"%s\")" % (line_index, line))
                    function_name = self.get_function_name(line, line_index)
                    if function_name in block_functions: function_recording = True
                    sound_type = None
                    continue
                if line.startswith(self.BLOCK_FUNCTION_END):
                    if sound_type is not None:
                        function_sounds[function_name] = sound_type
                    function_recording = False
                    continue
                if function_recording:
                    if self.SOUND_INDICATOR in line:
                        sound_type = line.split(self.SOUND_INDICATOR)[1].split(")")[0].split(",")[0]
                    module_name, is_module = self.get_module(line, line_index, is_function=True)
                    if is_module:
                        function_module[function_name] = module_name
        
        import_modules = self.get_import_modules(imports)
        if "WoodType" in import_modules:
            woodtype_sounds:dict[str,list[str]] = self.analyze_woodtype(version)
        if "BlockSetType" in import_modules:
            blocksettype_sounds:dict[str,str] = self.analyze_blocksettype(version)
        blocks:dict[str,dict[str,Any]] = {}
        code_to_block:dict[str,str] = {}
        start, end = line_starts[self.BLOCKS_TYPE], line_starts[self.FUNCTION_TYPE]
        for line_index, line in enumerate(file_contents[start:end]):
            # SECOND PASS, collect all info on blocks
            line = line.replace("\n", "").replace("(Block)", "")
            if not line.startswith(self.BLOCK_LINE): continue
            code_name = line.replace(self.BLOCK_LINE, "").split(" ")[0]
            block_name = line.split("\"")[1]
            code_to_block[code_name] = block_name

            if self.SOUND_INDICATOR in line:
                sound_type = line.split(self.SOUND_INDICATOR)[1].split(")")[0].split(",")[0]
                blocks[block_name] = {"sound_type": sound_type}
                continue

            function_name, is_function = self.get_block_function(line, line_index)
            if is_function:
                if function_name in function_sounds:
                    blocks[block_name] = {"sound_type": function_sounds[function_name]}
                    continue
                else: pass
            
            if self.COPY_INDICATOR in line:
                sound_type, has_sound_type = self.get_copy(blocks, code_to_block, line, line_index)
                if has_sound_type:
                    blocks[block_name] = {"sound_type": sound_type}
                    continue
                else: pass
            
            if self.WOODTYPE_INDICATOR in line:
                wood_type = line.split(self.WOODTYPE_INDICATOR)[1].split(")")[0].split(",")[0]
                if "hanging_sign" in line:
                    wood_block_type = self.HANGING_SIGN_WOOD_TYPE
                else: wood_block_type = self.WOOD_WOOD_TYPE
                wood_type_index = self.WOODTYPE_INDEXES[wood_block_type]
                blocks[block_name] = {"sound_type": woodtype_sounds[wood_type][wood_type_index]}
                continue

            if self.BLOCKSETTYPE_INDICATOR in line:
                blocksettype_type = line.split(self.BLOCKSETTYPE_INDICATOR)[1].split(")")[0].split(",")[0]
                blocks[block_name] = {"sound_type": blocksettype_sounds[blocksettype_type]}
                continue

            module_name, is_module = self.get_module(line, line_index, function_module)
            if is_module and module_name != "Block":
                importer = import_modules[module_name]
                importer_file = importer.replace(".", "/") + ".java"
                file_path = Searcher.full_path(version, "client", importer_file)
                with open(file_path, "rt") as f:
                    file_data = f.read()
                if self.MODULE_SOUND_TYPE_START in file_data:
                    sound_types = self.get_sound_type_from_module(file_data)
                    blocks[block_name] = {"sound_type": sound_types}
                    continue
                else: pass
            
            # ELSE
            blocks[block_name] = {"sound_type": "STONE"}

        blocks = Blocks0.sort_dict(blocks)
        return blocks

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,Any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        #print(blocks_file, os.path.join("./_versions", version, "client_decompiled", blocks_file), "\"" + os.path.join("./_versions", version, "client_decompiled") + "\"")
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        blocks = self.analyze(blocks_file_contents, version)
        if store: self.store(version, blocks, "blocks.json")
        return blocks

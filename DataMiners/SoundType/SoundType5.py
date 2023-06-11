import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

import DataMiners.SoundEvents.SoundEvents as SoundEvents

class SoundType5(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the path of Blocks.java (e.g. "nq.java")'''
        blocks_files = Searcher.search(version, "client", ["stone"], ["and"])
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s in SoundType:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s in SoundType!" % version)
        else: blocks_files = blocks_files[0]
        return blocks_files

    # def reverse_dictionary(self, dictionary:dict) -> dict:
    #     '''Turns {k: v} into {v: k}'''
    #     return dict([(value, key) for key, value in list(dictionary.items())])

    def analyze_subfunction_lines(self, line:str, version:str, variables:dict[str,str], subfunctions:dict[str,str]) -> str:
        '''Returns the purpose of the function, as "volume", "pitch", "dig", or "step"'''
        LINE_MATCH = {
            "return this.<volume>;": "volume",
            "return this.<pitch>;": "pitch",
            "return \"step.\" + this.<name>;": "step"
        }
        # subfunctions_reversed = self.reverse_dictionary(subfunctions)
        line_match_filled:dict[str,str] = {}
        for key, value in list(LINE_MATCH.items()):
            new_key = key.replace("<volume>", variables["volume"]).replace("<pitch>", variables["pitch"]).replace("<name>", variables["name"])
            line_match_filled[new_key] = value
        stripped_line = line.strip()
        if stripped_line in line_match_filled:
            function_purpose = line_match_filled[stripped_line]
        else: raise KeyError("Line \"%s\" in SoundType in %s could not have a purpose assigned!" % (stripped_line, version))
        already_has_step = "step" in subfunctions.values()
        if function_purpose == "step":
            if already_has_step: function_purpose = "step"
            else: function_purpose = "dig"
        return function_purpose

    def analyze_soundtype_function(self, file_contents:list[str], version:str) -> dict[str,str]:
        '''Returns the soundtype class name and the subfunction purposes (e.g. {"a": "volume"})'''
        FUNCTION_DECLARER = "public class "
        SUBFUNCTION_FLOAT_DECLARER = "    public float "
        SUBFUNCTION_STRING_DECLARER = "    public String "
        SUBFUNCTION_RECORDING_END = "    }"
        VARIABLE_DECLARER = "    public final "
        VARIABLE_ORDER = ["name", "volume", "pitch"]; VARIABLE_TYPES = ["String", "float", "float"]
        count = 0
        recording = False; recording_subfunction = False
        variables:dict[str,str] = {} # contains class variables that store name, volume, and pitch
        variable_count = 0 # how many variables have been recorded so far.
        subfunctions:dict[str,str] = {}
        subfunction_float_count = 0 # how many float subfunctions have been recorded so far.
        subfunction_string_count = 0 # ditto but strings
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(FUNCTION_DECLARER):
                if count > 0:
                    raise ValueError("Potential SoundType class in Blocks.java found multiple times in %s!" % version)
                count += 1
                recording = True
            if recording:
                if recording_subfunction:
                    if line.startswith(SUBFUNCTION_RECORDING_END):
                        if subfunction_line_count > 1:
                            raise ValueError("Too many lines in a subfunction \"%s\" in SoundType in %s:\n%s" % (subfunction_name, version, "\n".join(subfunction_lines)))
                        subfunctions[subfunction_name] = self.analyze_subfunction_lines(subfunction_lines[0], version, variables, subfunctions)
                        recording_subfunction = False
                    else:
                        subfunction_line_count += 1
                        subfunction_lines.append(line)
                elif line.startswith(VARIABLE_DECLARER):
                    split_line = line.replace(VARIABLE_DECLARER, "").split(" ")
                    variable_type = split_line[0]
                    variable_name = split_line[1].replace(";", "")
                    if variable_count > len(VARIABLE_ORDER) - 1:
                        raise KeyError("Too many variables in SoundType in %s!" % version)
                    if variable_type != VARIABLE_TYPES[variable_count]:
                        raise TypeError("Variable \"%s\" (%s) (what should be a %s) is instead type %s in SoundType in %s!" % (variable_name, VARIABLE_ORDER[variable_count], VARIABLE_TYPES[variable_count], variable_type, version))
                    variables[VARIABLE_ORDER[variable_count]] = variable_name
                    variable_count += 1
                elif line.startswith(SUBFUNCTION_FLOAT_DECLARER):
                    subfunction_name = line.replace(SUBFUNCTION_FLOAT_DECLARER, "").split("(")[0]
                    subfunction_line_count = 0
                    subfunction_lines:list[str] = []
                    recording_subfunction = True
                    subfunction_float_count += 1
                elif line.startswith(SUBFUNCTION_STRING_DECLARER):
                    subfunction_name = line.replace(SUBFUNCTION_STRING_DECLARER, "").split("(")[0]
                    subfunction_line_count = 0
                    subfunction_lines:list[str] = []
                    recording_subfunction = True
                    subfunction_string_count += 1
        if recording_subfunction: raise ValueError("Failed to end subfunction in SoundType before end of file in %s!" % version)
        if subfunction_float_count != 2:
            raise ValueError("Incorrect number of float subfunction lines in SoundType in %s: %s (should be 2)" % (version, subfunction_float_count))
        if subfunction_string_count != 2:
            raise ValueError("Incorrect number of string subfunction lines in SoundType in %s: %s (should be 2)" % (version, subfunction_string_count))
        return subfunctions

    def analyze_files_needed(self, file_contents:list[str], version:str) -> tuple[str,list[str]]:
        '''Returns the parent function and all other soundtype classes'''
        SOUNDTYPE_DECLARATION = "    public static final "
        END_RECORDING = "    protected "
        has_recorded = False
        base_class = None
        subclasses:list[str] = []
        for line in file_contents:
            line = line.rstrip()
            if "\"" not in line and has_recorded: break
            elif line.startswith(SOUNDTYPE_DECLARATION) and "\"" in line and "\"air\"" not in line:
                has_recorded = True
                split_line = line.replace(SOUNDTYPE_DECLARATION, "").split(" ")
                new_base_class = split_line[0]
                if base_class is None: base_class = new_base_class
                elif new_base_class != base_class:
                    raise ValueError("SoundType base class %s does not match %s in SoundType.Blocks (pass 1) in %s!" % (base_class, new_base_class, version))
                subclass = split_line[4].split("(")[0]
                if subclass not in subclasses and subclass != base_class: subclasses.append(subclass)
        else: raise ValueError("SoundType.Blocks (pass 1) did not break before reaching the end of the file in %s!" % version)
        if base_class is None: raise ValueError("SoundType.Blocks (pass 1) did not find base_class before reaching the end of the file in %s!" % version)
        return base_class, subclasses

    def analyze_subclass_soundtype(self, file_contents:list[str], file_name:str, version:str, base_functions:dict[str,str]) -> dict[str,str]:
        '''Returns a dict of function purposes and their value.'''
        STRING_FUNCTION_DECLARATION = "    public String "
        FLOAT_FUNCTION_DECLARATION = "    public float "
        RETURN_DECLARATION = "        return "
        output:dict[str,str] = {}
        write_count = 0
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(STRING_FUNCTION_DECLARATION):
                function_name = line.replace(STRING_FUNCTION_DECLARATION, "").split("(")[0]
            elif line.startswith(FLOAT_FUNCTION_DECLARATION):
                raise ValueError("Function changing volume or pitch found within subclass %s of SoundType in %s!" % (file_name, version))
            elif line.startswith(RETURN_DECLARATION):
                if "+" in line:
                    raise ValueError("\"+\" found in line \"%s\" in subclass %s of SoundType in %s!" % (file_name, version))
                elif (quote_count := line.count("\"")) != 2:
                    raise ValueError("\"\"\" found %s times in subclass %s of SoundType in %s instead of 2!" % (quote_count, file_name, version))
                write_count += 1
                sound_event = line.split("\"")[1]
                function_name = base_functions[function_name]
                output[function_name] = sound_event
        if write_count == 0:
            raise ValueError("No sound events were detected in subclass %s of SoundType in %s!" % (file_name, version))
        return output

    def get_file_contents(self, file_name:str, version:str) -> list[str]:
        with open(os.path.join("./_versions", version, "client_decompiled", file_name + ".java"), "rt") as f:
            return f.readlines()

    def get_float_value(self, value:str) -> float:
        '''Turns a Java float (e.g. "1.0f") into a Python float'''
        if not value.endswith("f"):
            raise ValueError("What should be a float value (\"%s\") does not end in \"f\"!" % value)
        return float(value.replace("f", ""))

    def get_string_value(self, value:str) -> str:
        '''Turns a Java string (e.g. \"\\\\\"hello\\\\\"\") into a Python string'''
        if not (value.endswith("\"") and value.startswith("\"")):
            raise ValueError("What should be a string value (\"%s\") does not start and/or end with \"\"\"!" % value)
        return value[1:-1] # removes just the start and end quotes

    def analyze_sound_types(self, file_contents:list[str], version:str, subclass_functions:dict[str,dict[str,str]], sound_type_file_name:str) -> dict[str,dict[str,int|str]]:
        SOUND_TYPE_DECLARATION = "    public static final %s " % sound_type_file_name
        RECORD_END = "    protected "
        has_recorded = False
        output:dict[str,dict[str,int|str]] = {}
        for line in file_contents:
            line = line.rstrip()
            if "\"" not in line and has_recorded: break
            elif line.startswith(SOUND_TYPE_DECLARATION):
                has_recorded = True
                if not line.endswith(";"):
                    raise ValueError("Line \"%s\" does not end in \";\" in SoundType.Blocks (pass 2) in %s!" % (line, version))
                split_line = line.replace(SOUND_TYPE_DECLARATION, "").split(" ")
                sound_type_name = split_line[0]
                subclass = split_line[3].split("(")[0]
                parameters = line.split("(")[-1].split(")")[0].split(", ")
                name, volume, pitch = parameters
                name = self.get_string_value(name); volume = self.get_float_value(volume); pitch = self.get_float_value(pitch)
                sound_type = {
                    "name": name,
                    "volume": volume,
                    "pitch": pitch,
                    "dig": "step." + name,
                    "step": "step." + name,
                }
                if subclass != sound_type_file_name:
                    sound_type.update(subclass_functions[subclass])
                output[sound_type_name] = sound_type
        else: raise ValueError("SoundType.Blocks (pass 2) did not break before reaching the end of the file in %s!" % version)
        if output == {}: raise ValueError("SoundType returned an empty dict in %s!" % version)
        return output

    def verify_sound_types(self, sound_types:dict[str,dict[str,int]], version:str) -> None:
        for sound_type_name, sound_type in list(sound_types.items()):
            if sound_type["dig"] == "random.glass" or sound_type["step"] == "random.glass":
                if sound_type["step"] == "random.glass":
                    raise ValueError("Sound type \"%s\" in %s has mis-matched dig and step variables: %s" % (sound_type_name, version, sound_type))
                else: break
        else: raise KeyError("Unable to find sound type with \"random.glass\" in %s!" % version)

    def analyze(self, blocks_file_contents:list[str], version:str) -> dict[str,dict[str,int|str]]:
        sound_type_base, sound_type_files = self.analyze_files_needed(blocks_file_contents, version)
        sound_type_base_file_contents = self.get_file_contents(sound_type_base, version)
        base_functions = self.analyze_soundtype_function(sound_type_base_file_contents, version)
        subclass_functions:dict[str,dict[str,str]] = {}
        for sound_type_file in sound_type_files:
            subclass_file_contents = self.get_file_contents(sound_type_file, version)
            subclass_functions[sound_type_file] = self.analyze_subclass_soundtype(subclass_file_contents, sound_type_file, version, base_functions)
        sound_types = self.analyze_sound_types(blocks_file_contents, version, subclass_functions, sound_type_base)
        self.verify_sound_types(sound_types, version)
        return sound_types

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,int|str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        sound_types = self.analyze(blocks_file_contents, version)
        if store: self.store(version, sound_types, "sound_types.json")
        return sound_types

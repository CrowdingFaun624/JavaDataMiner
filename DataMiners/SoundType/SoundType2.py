import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

import DataMiners.SoundEvents.SoundEvents as SoundEvents

class SoundType2(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.ignore_sound_events:list[str] = []
        if "ignore_sound_events" in kwargs:
            self.ignore_sound_events = kwargs["ignore_sound_events"]

    def search(self, version:str) -> str:
        '''Returns the path of Blocks.java (e.g. "afh.java")'''
        blocks_files = Searcher.search(version, "client", ["piston", "stone", "grass", "oak_stairs", "not:Bootstrap", "not:name_tag"], ["and"])
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s in SoundType:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s in SoundType!" % version)
        else: blocks_files = blocks_files[0]
        return blocks_files

    def reverse_dictionary(self, dictionary:dict) -> dict:
        '''Turns {k: v} into {v: k}'''
        return dict([(value, key) for key, value in list(dictionary.items())])

    def analyze_subfunction_lines(self, line:str, version:str, variables:dict[str,str], subfunctions:dict[str,str]) -> str:
        '''Returns the purpose of the function, as "volume", "pitch", "dig", "step", or "dig2"'''
        LINE_MATCH = {
            "return this.<volume>;": "volume",
            "return this.<pitch>;": "pitch",
            "return \"dig.\" + this.<name>;": "dig",
            "return \"step.\" + this.<name>;": "step"
        }
        subfunctions_reversed = self.reverse_dictionary(subfunctions)
        if "dig" in subfunctions_reversed: LINE_MATCH["return this.<digfunction>();"] = "dig2"
        replaces = {"<volume>": variables["volume"], "<pitch>": variables["pitch"], "<name>": variables["name"]}
        if "dig" in subfunctions_reversed: replaces["<digfunction>"] = subfunctions_reversed["dig"]
        stripped_line = line.strip()
        line_match_replaced = {}
        for key, value in list(LINE_MATCH.items()):
            replaced_key = key
            for replace_key, replace_value in list(replaces.items()):
                replaced_key = replaced_key.replace(replace_key, replace_value)
            line_match_replaced[replaced_key] = value
        if stripped_line not in line_match_replaced:
            raise KeyError("Line \"%s\" in SoundType in %s not found in the following lines:\n\"%s\"" % (stripped_line, version, "\"\n\"".join(line_match_replaced)))
        return line_match_replaced[stripped_line]

    def analyze_soundtype_function(self, file_contents:list[str], version:str) -> tuple[str,dict[str,str]]:
        '''Returns the soundtype class name and the subfunction purposes (e.g. {"a": "volume"})'''
        def fail_to_break_error() -> None:
            raise ValueError("Failed to end subfunction in SoundType before end of file in %s!" % version)
        FUNCTION_DECLARER = "    public static class "
        SUBFUNCTION_FLOAT_DECLARER = "        public float "
        SUBFUNCTION_STRING_DECLARER = "        public String "
        SUBFUNCTION_RECORDING_END = "        }"
        VARIABLE_DECLARER = "        public final "
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
                function_name = line.replace(FUNCTION_DECLARER, "").split(" ")[0]
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
        else: fail_to_break_error()
        if recording_subfunction: fail_to_break_error()
        if subfunction_float_count != 2:
            raise ValueError("Incorrect number of float subfunction lines in SoundType in %s: %s (should be 2)" % (version, subfunction_float_count))
        if subfunction_string_count != 3:
            raise ValueError("Incorrect number of string subfunction lines in SoundType in %s: %s (should be 3)" % (version, subfunction_string_count))
        return function_name, subfunctions

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

    def get_default_sound_events(self, name:str) -> tuple[str,str,str]:
        '''Returns the default dig, step, and dig2 sound events of a name'''
        return "dig." + name, "step." + name, "dig." + name

    def verify_sound_events(self, sound_types:dict[str,dict[str,int|str]], sound_events:list[str], version) -> None:
        '''Raises an error if a sound event in the sound type data does not exist'''
        SOUND_EVENT_KEYS = ["dig", "step", "dig2"]
        for sound_type_name, sound_type in list(sound_types.items()):
            for sound_event_key in SOUND_EVENT_KEYS:
                sound_event = sound_type[sound_event_key]
                sound_event_exists = sound_event in sound_events
                if not sound_event_exists and sound_event not in self.ignore_sound_events:
                    raise KeyError("Sound event \"%s\" in %s's %s in SoundType in %s does not exist!" % (sound_event, sound_type_name, sound_event_key, version))
                elif sound_event_exists and sound_event in self.ignore_sound_events:
                    raise KeyError("Sound event \"%s\" (which is on the ignore list) in %s's %s in SoundType in %s exists!" % (sound_event, sound_type_name, sound_event_key, version))

    def analyze(self, file_contents:list[str], version:str, sound_events:list[str]) -> list[dict[str,int|str]]:
        END_RECORDING = "    protected "
        SUBFUNCTIONS_END = "    };"
        SOUND_EVENT_DECLARATION = "            return "
        SUBFUNCTION_DECLARATION = "        public String "
        function_name, subfunctions = self.analyze_soundtype_function(file_contents, version)
        sound_type_declaration = "    public static final " + function_name + " "
        recording = True
        recording_subfunctions = False
        sound_types:dict[str,dict[str,int|str]] = {}
        for line in file_contents:
            line = line.rstrip()
            if recording_subfunctions:
                if line.startswith(SUBFUNCTIONS_END): recording_subfunctions = False; continue
                elif line.startswith(SUBFUNCTION_DECLARATION):
                    current_subfunction = line.replace(SUBFUNCTION_DECLARATION, "").split("(")[0]
                elif line.startswith(SOUND_EVENT_DECLARATION):
                    sound_event = self.get_string_value(line.replace(SOUND_EVENT_DECLARATION, "")[:-1]) # [:-1] is to remove semicolon
                    if sound_event not in sound_events:
                        raise KeyError("Sound event \"%s\" is not a valid sound event in SoundType in %s!" % (sound_event, version))
                    sound_types[sound_type_code_name][subfunctions[current_subfunction]] = sound_event
                    if subfunctions[current_subfunction] == "dig":
                        if not has_modified_dig2:
                            sound_types[sound_type_code_name]["dig2"] = sound_event
                    elif subfunctions[current_subfunction] == "dig2":
                        has_modified_dig2 = True
            elif line.startswith(sound_type_declaration):
                sound_type_code_name = line.replace(sound_type_declaration, "").split(" ")[0]
                parameters = line.split("(")[1].split(")")[0].split(", ")
                sound_type_name = self.get_string_value(parameters[0])
                sound_type_volume = self.get_float_value(parameters[1])
                sound_type_pitch = self.get_float_value(parameters[2])
                sound_type_dig, sound_type_step, sound_type_dig2 = self.get_default_sound_events(sound_type_name)
                sound_types[sound_type_code_name] = {"name": sound_type_name,
                                                "volume": sound_type_volume,
                                                "pitch": sound_type_pitch,
                                                "dig": sound_type_dig,
                                                "step": sound_type_step,
                                                "dig2": sound_type_dig2}
                has_modified_dig2 = False
                if line.endswith(";"): # no expansion
                    continue
                elif line.endswith("{"): # thing that overrides the base function
                    recording_subfunctions = True
                else:
                    raise ValueError("Weird character found at the end of line in SoundType in %s: \"%s\"" % (version, line))
            elif line.startswith(END_RECORDING) and recording:
                recording = False; break
        else: # if it did not break before reaching the end of the file
            raise ValueError("SoundType did not break before reaching the end of the file in %s!" % version)
        self.verify_sound_events(sound_types, sound_events, version)
        return sound_types

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,int|str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        sound_events = SoundEvents.SoundEvents.get_data_file(version)
        if not isinstance(sound_events, list): raise TypeError("SoundEvents subprocess of SoundType gave code keys in %s!" % version)
        sound_type_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", sound_type_file), "rt") as f:
            sound_type_file_contents = f.readlines()
        sound_types = self.analyze(sound_type_file_contents, version, sound_events)
        if store: self.store(version, sound_types, "sound_types.json")
        return sound_types

import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

class SoundTypeNew(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the file path of the desired file.'''
        sound_events_file:list[str] = Searcher.search(version, "client", ["only:file:SoundType.java"], allow_decompile=True)
        if len(sound_events_file) > 1:
            print("\n".join(sound_events_file))
            raise FileExistsError("Too many files SoundEvents files found for %s" % version)
        elif len(sound_events_file) == 0:
            raise FileNotFoundError("No SoundEvents file found for %s" % version)
        else: sound_events_file:str = sound_events_file[0]
        return sound_events_file
    
    def format_parameters(parameters:list[str], code_name:str="") -> list[float|str]:
        '''Replaces volume and pitch with equivalent float; removes "SoundEvents." from sound events'''
        output:list[float|str] = []
        for index, parameter in enumerate(parameters):
            if index in (0, 1): # volume/pitch
                if not parameter.endswith("f"): raise ValueError("Volume/pitch \"%s\" in sound type \"%s\" does not end with \"f\"!" % (parameter, code_name))
                output.append(float(parameter.replace("f", "")))
            else: # Sounds
                if not parameter.startswith("SoundEvents."):
                    raise ValueError("Sound event \"%s\" in sound type \"\" does not start with \"SoundEvents.\"!" % (parameter, code_name))
                output.append(parameter.replace("SoundEvents.", ""))
        return output
        

    def analyze(self, file_contents:list[str]) -> dict[str,dict[str,float|str]]:
        '''Takes in the lines of SoundType.java, and returns its sound types'''
        RECORD_START = "public class SoundType {"
        VALID_LINE_START = "    public static final SoundType "
        PARAMETER_NAMES = ["volume", "pitch", "break", "step", "place", "hit", "fall"]
        
        sound_types:dict[str,dict[str,float|str]] = {}
        is_recording = False
        for line in file_contents:
            line = line.replace("\n", "")
            if line == RECORD_START:
                if is_recording: raise ValueError("Found start string multiple times!")
                else: is_recording = True
                continue
            if is_recording: # MAIN CONTENT
                if not line.startswith(VALID_LINE_START):
                    is_recording = False
                    break # no content after the main content is needed.
                code_name = line.replace(VALID_LINE_START, "").split(" ")[0]
                parameters = line.split("(")[1].replace(");", "").split(", ")
                parameters = SoundTypeNew.format_parameters(parameters, code_name)
                sound_types[code_name] = dict(zip(PARAMETER_NAMES, parameters))
        sound_types = SoundTypeNew.sort_dict(sound_types)
        return sound_types

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,float|str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        sound_type_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", sound_type_file), "rt") as f:
            sound_type_file_contents = f.readlines()
        sound_types = self.analyze(sound_type_file_contents)
        if store: self.store(version, sound_types, "sound_types.json")
        return sound_types

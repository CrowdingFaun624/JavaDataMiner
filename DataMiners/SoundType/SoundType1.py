import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

import DataMiners.SoundEvents.SoundEvents as SoundEvents

class SoundType1(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the path of SoundType.java (e.g. "btd.java")'''
        sound_events_name = DataMiner.get_file_name_from_path(DataMiner.get_dataminer(version, SoundEvents.dataminers).search(version)) # name of SoundEvents.java
        sound_type_files = Searcher.search(version, "client", ["count(==,14):this", "count(>=,60):" + sound_events_name + ".", "not:file:" + sound_events_name], ["and"])
        if len(sound_type_files) > 1:
            raise FileExistsError("Too many SoundType files found for %s (SoundEvents.java is \"%s\"):\n%s" % (version, sound_events_name, "\n".join(sound_type_files)))
        elif len(sound_type_files) == 0:
            raise FileNotFoundError("No SoundType file found for %s (SoundEvents.java is \"%s\")!" % (version, sound_events_name))
        else: sound_type_files = sound_type_files[0]
        return sound_type_files

    def analyze(self, version:str, file_contents:str, sound_events:dict[str,str]) -> dict[str,dict[str,int|str]]:
        RECORD_START = "public class "
        RECORD_END = "public final "
        SOUND_TYPE_DECLARE = "public static final "
        PARAMETER_NAMES = ["volume", "pitch", "break", "step", "place", "hit", "fall"]
        recording = False
        output:dict[str,dict[str,int|str]] = {}
        for line in file_contents:
            line = line.strip()
            if line.startswith(RECORD_START):
                if recording: raise ValueError("SoundType in %s gave two recording start lines!" % version)
                recording = True
            elif line.startswith(RECORD_END): recording = False; break
            else:
                if not recording: continue
                if not line.startswith(SOUND_TYPE_DECLARE): raise ValueError("Strange line encountered in SoundType in %s: \"%s\"" % (version, line))
                stripped_line = line.replace(SOUND_TYPE_DECLARE, "")
                stripped_line = stripped_line.split(" ")
                code_name = stripped_line[1]
                parameters = " ".join(stripped_line[4:]).split("(")[-1].split(")")[0].split(", ")
                if len(parameters) != 7: raise ValueError("Wrong number of SoundType parameters in %s: \"%s\"" % (version, line))
                volume = float(parameters[0].replace("f", ""))
                pitch = float(parameters[1].replace("f", ""))
                sound_event_parameters = parameters[2:]
                sound_event_parameters = [parameter.split(".")[-1] for parameter in sound_event_parameters] # remove "zo." from "zo.h" or whatever
                sound_event_parameters = [sound_events[parameter] for parameter in sound_event_parameters] # replace with in-game names
                output[code_name] = dict(zip(PARAMETER_NAMES, [volume, pitch, *sound_event_parameters]))
        return output

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,int|str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        sound_events = SoundEvents.get_data_file(version)
        if not isinstance(sound_events, dict): raise TypeError("SoundEvents subprocess of SoundType did not give code keys in %s!" % version)
        sound_type_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", sound_type_file), "rt") as f:
            sound_type_file_contents = f.readlines()
        sound_types = self.analyze(version, sound_type_file_contents, sound_events)
        if store: self.store(version, sound_types, "sound_types.json")
        return sound_types

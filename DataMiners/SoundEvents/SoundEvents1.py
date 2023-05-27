import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

class SoundEvents1(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the path of SoundEvents.java (e.g. "zo.java")'''
        sound_events_files = Searcher.search(version, "client", ["block.stone.hit", "hit.stone"])
        if len(sound_events_files) > 1:
            raise FileExistsError("Too many SoundEvents files found for %s:\n%s" % (version, "\n".join(sound_events_files)))
        elif len(sound_events_files) == 0:
            raise FileNotFoundError("No SoundEvents file found for %s" % version)
        else: sound_events_files = sound_events_files[0]
        return sound_events_files

    def analyze(self, file_contents:list[str], version:str) -> dict[str,str]:
        START_SOUND_EVENTS = "public class "
        END_SOUND_EVENTS = ""
        VALID_EVENT_START = "public static final "
        recording = False
        output = {}
        for line in file_contents:
            line = line.strip()
            if line.startswith(START_SOUND_EVENTS):
                if recording: raise ValueError("Start recording line for sound events encountered twice in %s!" % version)
                recording = True
            elif line == END_SOUND_EVENTS and recording:
                recording = False
                break
            else:
                if not recording: continue
                if not line.startswith(VALID_EVENT_START): raise ValueError("Strange line encountered in sound events in %s: \"%s\"" % (version, line))
                stripped_line = line.replace(VALID_EVENT_START, "", 1)
                stripped_line = stripped_line.split(" ")
                code_name = stripped_line[1]
                game_name = stripped_line[-1].split("(")[-1].split(")")[0].replace("\"", "")
                output[code_name] = game_name
        output = DataMiner.DataMiner.sort_dict(output, by_values=True)
        return output

    def activate(self, version:str, store:bool=True) -> dict[str,str]|list[str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        sound_events_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", sound_events_file), "rt") as f:
            sound_events_file_contents = f.readlines()
        sound_events = self.analyze(sound_events_file_contents, version)
        if store: self.store(version, sound_events, "sound_events.json")
        return sound_events

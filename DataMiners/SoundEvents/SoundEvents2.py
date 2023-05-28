import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

class SoundEvents2(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the path of the larger SoundEvents.java file (e.g. "wj.java")'''
        sound_events_files = Searcher.search(version, "client", ["block.stone.hit", "Bootstrap"], ["and"])
        if len(sound_events_files) > 1:
            raise FileExistsError("Too many SoundEvents files found for %s:\n%s" % (version, "\n".join(sound_events_files)))
        elif len(sound_events_files) == 0:
            raise FileNotFoundError("No SoundEvents file found for %s" % version)
        else: sound_events_files = sound_events_files[0]
        return sound_events_files
    
    def analyze(self, file_contents:list[str], version:str) -> dict[str,str]:
        RECORD_START = "            throw new RuntimeException(\"Accessed Sounds before Bootstrap!\");"
        RECORD_END = "    }"
        SKIP_LINES = ["        }"]
        recording = False
        output:dict[str,str] = {}
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(RECORD_START):
                if recording:
                    raise ValueError("Starting line in SoundEvents in %s encountered twice!" % version)
                recording = True
            elif line.startswith(RECORD_END) and recording: recording = False; break
            else:
                if not recording: continue
                if line in SKIP_LINES: continue
                stripped_line = line.strip().split(" ")
                code_name = stripped_line[0]
                game_name = stripped_line[-1].split("\"")[-2]
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

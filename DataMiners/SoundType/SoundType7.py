import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

import DataMiners.SoundEvents.SoundEvents as SoundEvents

class SoundType7(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the path of Blocks.java (e.g. "nq.java")'''
        blocks_files = Searcher.search(version, "client", ["stone"], ["and"])
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Blocks files found for %s in SoundType:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Blocks file found for %s in SoundType!" % version)
        else: blocks_files = blocks_files[0]
        return blocks_files

    def parse_string(self, value:str, version:str) -> str:
        if not value.startswith("\"") or not value.endswith("\""): raise ValueError("Apparently string value \"%s\" does not start and end with quotes in SoundType in %s!" % (value, version))
        return value[1:-1]
    
    def parse_float(self, value:str, version:str) -> float:
        if not value.endswith("f"): raise ValueError("Apparently float value \"%s\" does not end with \"f\" in SoundType in %s!" % (value, version))
        return float(value.replace("f", ""))

    def analyze(self, file_contents:list[str], version:str) -> dict[str,dict[str,int|str]]:
        SOUND_TYPE_DECLARER = "    private static "
        sound_type_class = None
        output:dict[str,dict[str,int|str]] = {}
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(SOUND_TYPE_DECLARER):
                split_line = line.replace(SOUND_TYPE_DECLARER, "").split(" ")
                if sound_type_class is None: sound_type_class = split_line[0]
                elif split_line[0] != sound_type_class: raise ValueError("Sound type class apparently \"%s\" for line \"%s\" when it should be \"%s\" in SoundType in %s!" % (split_line[0], line, sound_type_class, version))
                code_name = split_line[1]
                if "(" not in line or ")" not in line: raise ValueError("Line \"%s\" in SoundType in %s is not a valid sound type line!" % (line, version))
                parameters = line.split("(")[1].split(")")[0]
                if parameters.count(",") != 2: raise ValueError("Line \"%s\" has an incorrect number of parameters in SoundType in %s!" % (line, version))
                parameters = parameters.split(", ")
                name, volume, pitch = self.parse_string(parameters[0], version), self.parse_float(parameters[1], version), self.parse_float(parameters[2], version)
                output[code_name] = {
                    "name": name,
                    "volume": volume,
                    "pitch": pitch,
                    "dig": "step." + name,
                    "step": "step." + name
                }
            else:
                if len(output) > 0: break
        else: raise ValueError("Failed to start/stop recording in SoundType in %s!" % version)
        return output

    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,int|str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            blocks_file_contents = f.readlines()
        sound_types = self.analyze(blocks_file_contents, version)
        if store: self.store(version, sound_types, "sound_types.json")
        return sound_types
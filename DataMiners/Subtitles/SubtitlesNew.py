import json
import os

import DataMiners.DataMiner as DataMiner
import DataMiners.Language.Language as Language

class SubtitlesNew(DataMiner.DataMiner):
    def activate(self, version:str, store:bool=True) -> dict[str,str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        language_data:dict[str,str] = Language.get_data_file(version)
        subtitles = {}
        for key, value in list(language_data.items()):
            if not key.startswith("subtitles."): continue
            subtitles[key] = value
        if store: self.store(version, subtitles, "subtitles.json")
        return subtitles

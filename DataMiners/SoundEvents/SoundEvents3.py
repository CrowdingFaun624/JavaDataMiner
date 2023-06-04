import os

import DataMiners.DataMiner as DataMiner
import Importer.AssetImporter as AssetImporter

class SoundEvents3(DataMiner.DataMiner):
    def analyze(self, sounds_json:dict[str,dict[str,any]], version:str) -> list[str]:
        if not isinstance(sounds_json, dict):
            raise TypeError("sounds.json is not a list in SoundEvents in %s!" % version)
        output = list(sounds_json.keys())
        for key in output:
            if not isinstance(key, str): raise TypeError("Key \"%s\" in sounds.json in SoundEvents in %s is not a string!" % (key, version))
        return sorted(output)

    def activate(self, version:str, store:bool=True) -> dict[str,str]|list[str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        sounds_json_file = AssetImporter.get_asset_version(version, "minecraft/sounds.json", "j")
        sound_events = self.analyze(sounds_json_file, version)
        if store: self.store(version, sound_events, "sound_events.json")
        return sound_events

import DataMiners.DataMiner as DataMiner

class SoundType9(DataMiner.DataMiner):
    def activate(self, version:str, store:bool=True) -> dict[str,dict[str,int|str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        sound_types = {
            "a": {
                "name": "stone",
                "volume": 1.0,
                "pitch": 1.0,
                "dig": "step.stone",
                "step": "step.stone"
            },
            "b": {
                "name": "wood",
                "volume": 1.0,
                "pitch": 1.0,
                "dig": "step.wood",
                "step": "step.wood"
            },
            "c": {
                "name": "gravel",
                "volume": 1.0,
                "pitch": 1.0,
                "dig": "step.gravel",
                "step": "step.gravel"
            },
            "av": {
                "name": "grass",
                "volume": 1.0,
                "pitch": 1.0,
                "dig": "step.grass",
                "step": "step.grass"
            },
            "aw": {
                "name": "stone",
                "volume": 1.0,
                "pitch": 1.0,
                "dig": "step.stone",
                "step": "step.stone"
            },
            "ax": {
                "name": "stone",
                "volume": 1.0,
                "pitch": 1.5,
                "dig": "step.stone",
                "step": "step.stone"
            }
        }
        if store: self.store(version, sound_types, "sound_types.json")
        return sound_types
# you gotta do what you gotta do
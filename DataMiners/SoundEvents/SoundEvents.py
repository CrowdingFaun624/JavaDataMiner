import json
import os

import DataMiners.DataMiner as DataMiner

import DataMiners.SoundEvents.SoundEventsNew as SoundEventsNew
import DataMiners.SoundEvents.SoundEvents1 as SoundEvents1
import DataMiners.SoundEvents.SoundEvents2 as SoundEvents2
import DataMiners.SoundEvents.SoundEvents3 as SoundEvents3

dataminers:list[DataMiner.DataMiner] = [
    SoundEventsNew.SoundEventsNew("19w36a", "-"),
    SoundEvents1.SoundEvents1("19w34a", "19w35a"),
    SoundEventsNew.SoundEventsNew("1.14.4", "1.14.4"),
    SoundEvents1.SoundEvents1("18w43a", "1.14.4-pre7"),
    SoundEvents2.SoundEvents2("15w49b", "1.13.2"),
    SoundEvents3.SoundEvents3("1.8.9", "1.8.9"),
    SoundEvents2.SoundEvents2("15w43a", "15w49a"),
    SoundEvents3.SoundEvents3("14w25a", "15w42a", sounds_json_name="minecraft/sounds.json"),
    SoundEvents3.SoundEvents3("14w20a", "14w21b", sounds_json_name="sounds.json"),
    SoundEvents3.SoundEvents3("1.7.10-pre4", "1.7.10", sounds_json_name="minecraft/sounds.json"), # idk why it keeps switching
    SoundEvents3.SoundEvents3("-", "1.7.10-pre3", sounds_json_name="sounds.json"),
]
# TODO: it is possible for the two sound files to differ. Make sure they are documented anyways.
def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,str]:
    '''Returns the sound events data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "sound_events.json", dataminers, redo, kwargs)

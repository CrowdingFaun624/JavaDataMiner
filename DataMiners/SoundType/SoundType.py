import DataMiners.DataMiner as DataMiner

import DataMiners.SoundType.SoundTypeNew as SoundTypeNew
import DataMiners.SoundType.SoundType1 as SoundType1

dataminers:list[DataMiner.DataMiner] = [
    SoundTypeNew.SoundTypeNew("19w36a", "-"),
    SoundType1.SoundType1("19w34a", "19w35a"),
    SoundTypeNew.SoundTypeNew("1.14.4", "1.14.4"),
    SoundType1.SoundType1("-", "1.14.4-pre7")
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,dict[str,int|str]]:
    '''Returns the sound types data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "sound_types.json", dataminers, redo, kwargs)

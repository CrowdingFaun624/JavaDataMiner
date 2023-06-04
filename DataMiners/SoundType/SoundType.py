import DataMiners.DataMiner as DataMiner

import DataMiners.SoundType.SoundTypeNew as SoundTypeNew
import DataMiners.SoundType.SoundType1 as SoundType1
import DataMiners.SoundType.SoundType2 as SoundType2

dataminers:list[DataMiner.DataMiner] = [
    SoundTypeNew.SoundTypeNew("19w36a", "-"),
    SoundType1.SoundType1("19w34a", "19w35a"),
    SoundTypeNew.SoundTypeNew("1.14.4", "1.14.4"),
    SoundType1.SoundType1("15w49b", "1.14.4-pre7"),
    SoundType2.SoundType2("1.8.9", "1.8.9", ignore_sound_events=["step.anvil"]), # sound types begin being included in Blocks.java; MC-7849
    SoundType1.SoundType1("15w43a", "15w49a"),
    SoundType2.SoundType2("-", "15w42a", ignore_sound_events=["step.anvil"])
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,dict[str,int|str]]:
    '''Returns the sound types data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "sound_types.json", dataminers, redo, kwargs)

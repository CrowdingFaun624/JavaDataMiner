import DataMiners.DataMiner as DataMiner

import DataMiners.SoundTypeBlocks.SoundTypeBlocksNew as SoundTypeBlocksNew

dataminers:list[DataMiner.DataMiner] = [
    SoundTypeBlocksNew.SoundTypeBlocksNew("19w36a", "-", blocks_sound_type_variable="sound_type"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("19w34a", "19w35a", blocks_sound_type_variable="sound_type_code_name"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("1.14.4", "1.14.4", blocks_sound_type_variable="sound_type"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("-", "1.14.4-pre7", blocks_sound_type_variable="sound_type_code_name")
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,list[str]]:
    '''Returns the sound type blocks data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "sound_type_blocks.json", redo, dataminers, kwargs)

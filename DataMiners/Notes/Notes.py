import DataMiners.DataMiner as DataMiner

import DataMiners.Notes.NotesNew as NotesNew

dataminers:list[DataMiner.DataMiner] = [ # this thing is intended to help make SoundEvents pre-1.6 more accurate
    NotesNew.NotesNew("-", "13w23b")
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> list[str]:
    '''Returns the notes data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "notes.json", dataminers, redo, kwargs)

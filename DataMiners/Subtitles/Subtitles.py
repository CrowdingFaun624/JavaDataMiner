import DataMiners.DataMiner as DataMiner

import DataMiners.Subtitles.SubtitlesNew as SubtitlesNew

dataminers:list[DataMiner.DataMiner] = [
    SubtitlesNew.SubtitlesNew("15w43b", "-")
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,str]:
    '''Returns the subtitles data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "subtitles.json", dataminers, redo, kwargs)

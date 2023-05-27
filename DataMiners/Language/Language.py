import json
import os

import DataMiners.DataMiner as DataMiner

import DataMiners.Language.Language1 as Language1
import DataMiners.Language.LanguageNew as LanguageNew

dataminers:list[DataMiner.DataMiner] = [
    Language1.Language1("b1.0", "18w01a"),
    LanguageNew.LanguageNew("18w02a", "-")
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,str]:
    '''Returns the language data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "language.json", dataminers, redo, kwargs)

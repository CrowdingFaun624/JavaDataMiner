import json
import os

import DataMiners.DataMiner as DataMiner

import DataMiners.Blocks.Blocks2 as Blocks2
import DataMiners.Blocks.Blocks1 as Blocks1
import DataMiners.Blocks.BlocksNew as BlocksNew

dataminers:list[DataMiner.DataMiner] = [
    BlocksNew.BlocksNew("19w36a", "-"),
    Blocks1.Blocks1("19w34a", "19w35a"),
    BlocksNew.BlocksNew("1.14.4", "1.14.4"),
    Blocks1.Blocks1("18w43a", "1.14.4-pre7"),
    Blocks2.Blocks2("17w50a", "1.13.2",
                    record_start_threshold=3,
                    blocks_search_query=["air", "stone", "granite", "polished_granite", "not:Name", "not:nocaps:hashMap", "not:Bootstrap"],
                    blocks_list_search_query=["air", "stone", "granite", "polished_granite", "Bootstrap"],
                    remove_air=True),
    Blocks2.Blocks2("17w47a", "17w49b", # post-flattening
                    record_start_threshold=2,
                    blocks_search_query=["air", "stone", "granite", "polished_granite", "not:Name", "not:nocaps:hashMap", "not:Bootstrap"],
                    blocks_list_search_query=["air", "stone", "granite", "polished_granite", "Bootstrap"],
                    remove_air=True),
    Blocks2.Blocks2("-", "17w46a", # pre-flattening
                    record_start_threshold=2,
                    blocks_search_query=["stone", "grass", "leaves", "dispenser", "not:name_tag", "not:Bootstrap"],
                    blocks_list_search_query=["stone", "grass", "leaves", "dispenser", "not:name_tag", "Bootstrap"],
                    remove_air=False)
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,dict[str,any]]:
    '''Returns the blocks data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "blocks.json", dataminers, redo, kwargs)

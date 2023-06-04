import json
import os

import DataMiners.DataMiner as DataMiner

import DataMiners.Blocks.Blocks4 as Blocks4
import DataMiners.Blocks.Blocks3 as Blocks3
import DataMiners.Blocks.Blocks2 as Blocks2
import DataMiners.Blocks.Blocks1 as Blocks1
import DataMiners.Blocks.BlocksNew as BlocksNew

dataminers:list[DataMiner.DataMiner] = [
    BlocksNew.BlocksNew("19w36a", "-"),
    Blocks1.Blocks1("19w34a", "19w35a"),
    BlocksNew.BlocksNew("1.14.4", "1.14.4"),
    Blocks1.Blocks1("18w43a", "1.14.4-pre7"),
    Blocks2.Blocks2("17w50a", "1.13.2", record_start_threshold=3),
    Blocks2.Blocks2("17w47a", "17w49b", record_start_threshold=2), # post-flattening
    Blocks3.Blocks3("15w49b", "17w46a"), # pre-flattening
    Blocks4.Blocks4("1.8.9", "1.8.9",
                    blocks_list_record_threshold=1,
                    sound_type_overrides={"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "acacia_stairs": "wood", "dark_oak_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone", "red_sandstone_stairs": "stone"}), # pre-subtitles renaming & sound type code restructuring
    Blocks3.Blocks3("15w43a", "15w49a"),
    Blocks4.Blocks4("-", "15w42a",
                    blocks_list_record_threshold=2,
                    sound_type_overrides={"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "acacia_stairs": "wood", "dark_oak_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone", "red_sandstone_stairs": "stone", "purpur_stairs": "stone"})
]

def get_data_file(version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> dict[str,dict[str,any]]:
    '''Returns the blocks data file for this version, creating it if it does not exist.'''
    return DataMiner.get_data_file(version, "blocks.json", dataminers, redo, kwargs)

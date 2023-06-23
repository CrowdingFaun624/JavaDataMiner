import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.SoundTypeBlocks.SoundTypeBlocksNew as SoundTypeBlocksNew

dataminers:list[DataMiner.DataMiner] = [
    SoundTypeBlocksNew.SoundTypeBlocksNew("19w36a", "-", blocks_sound_type_variable="sound_type"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("1.14_combat-0", "19w35a", blocks_sound_type_variable="sound_type_code_name"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("1.14.4", "1.14.4", blocks_sound_type_variable="sound_type"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("15w49b", "1.14.4-pre7", blocks_sound_type_variable="sound_type_code_name"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("1.8.9", "1.8.9", blocks_sound_type_variable="sound_type"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("15w43a", "15w49a", blocks_sound_type_variable="sound_type_code_name"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("in-20100125-1", "15w42a", blocks_sound_type_variable="sound_type"),
    NoneDataMiner.NoneDataMiner("in-20100111-1", "in-20100111-1"),
    SoundTypeBlocksNew.SoundTypeBlocksNew("in-20100105", "in-20100105", blocks_sound_type_variable="sound_type"),
    NoneDataMiner.NoneDataMiner("-", "in-20091231-2"),
]

SoundTypeBlocks = DataMinerType.DataMinerType("sound_type_blocks.json", dataminers)

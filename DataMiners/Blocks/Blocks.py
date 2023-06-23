import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.Blocks.Blocks9 as Blocks9
import DataMiners.Blocks.Blocks8 as Blocks8
import DataMiners.Blocks.Blocks7 as Blocks7
import DataMiners.Blocks.Blocks6 as Blocks6
import DataMiners.Blocks.Blocks5 as Blocks5
import DataMiners.Blocks.Blocks4 as Blocks4
import DataMiners.Blocks.Blocks3 as Blocks3
import DataMiners.Blocks.Blocks2 as Blocks2
import DataMiners.Blocks.Blocks1 as Blocks1
import DataMiners.Blocks.BlocksNew as BlocksNew

SOUND_TYPE_OVERRIDES1 = {"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "acacia_stairs": "wood", "dark_oak_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone", "red_sandstone_stairs": "stone", "purpur_stairs": "stone"}
SOUND_TYPE_OVERRIDES2 = {"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "acacia_stairs": "wood", "dark_oak_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone", "red_sandstone_stairs": "stone"}
SOUND_TYPE_OVERRIDES3 = {"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "acacia_stairs": "wood", "dark_oak_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone"}
SOUND_TYPE_OVERRIDES4 = {"oak_stairs": "wood", "spruce_stairs": "wood", "birch_stairs": "wood", "jungle_stairs": "wood", "stone_stairs": "stone", "brick_stairs": "stone", "stone_brick_stairs": "stone", "nether_brick_stairs": "stone", "sandstone_stairs": "stone", "cobblestone_wall": "stone", "quartz_stairs": "stone"}
SOUND_TYPE_OVERRIDES5 = {"minecraft:stairs_oak": "wood", "minecraft:stairs_wood_spruce": "wood", "minecraft:stairs_wood_birch": "wood", "minecraft:stairs_wood_jungle": "wood", "minecraft:stairs_stone": "stone", "minecraft:stair_brick": "stone", "minecraft:stair_stonebrick": "stone", "minecraft:stairs_netherbrick": "stone", "minecraft:stairs_sandstone": "stone", "minecraft:wall_cobble": "stone", "minecraft:stairs_quartz": "stone"} # i am dying it says "stair_brick" instead of "stairs_brick"
SOUND_TYPE_ALLOWANCES1 = ["air", "flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "barrier"]
SOUND_TYPE_ALLOWANCES2 = ["air", "flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "barrier", "bed"] # MC-66347
SOUND_TYPE_ALLOWANCES3 = ["air", "flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "barrier", "bed", "slime"] # MC-44859
SOUND_TYPE_ALLOWANCES4 = ["air", "flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "barrier", "bed", "slime", "end_portal", "command_block", "brewing_stand", "flower_pot", "beacon", "piston_extension", "noteblock", "enchanting_table"] # these blocks were troubling in development of Blocks4
SOUND_TYPE_ALLOWANCES5 = ["air", "flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "bed", "end_portal", "command_block", "brewing_stand", "flower_pot", "beacon", "piston_extension", "noteblock", "enchanting_table"]
SOUND_TYPE_ALLOWANCES6 = ["flowing_water", "water", "flowing_lava", "lava", "web", "redstone_wire", "monster_egg", "cauldron", "tripwire_hook", "tripwire", "bed", "end_portal", "command_block", "brewing_stand", "flower_pot", "beacon", "piston_extension", "noteblock", "enchanting_table"] # air was made a block internally in 13w38b
SOUND_TYPE_ALLOWANCES7 = ["minecraft:water_flow", "minecraft:water_still", "minecraft:lava_flow", "minecraft:lava_still", "minecraft:web", "minecraft:redstone_dust", "minecraft:monster_egg", "minecraft:cauldron", "minecraft:trip_wire", "minecraft:trip_wire_source", "minecraft:bed", "minecraft:portal_end", "minecraft:command_block", "minecraft:brewing_stand", "minecraft:flower_pot", "minecraft:beacon", "minecraft:piston_moving_piece", "minecraft:noteblock", "minecraft:enchanting_table"] # this shook things up quite a bit didn't it
SOUND_TYPE_ALLOWANCES8 = ["water_flow", "water_still", "lava_flow", "lava_still", "noteblock", "bed", "web", 36, 97, "enchanting_table", "brewing_stand", "cauldron", 119, "trip_wire_source", "trip_wire", "command_block", "beacon", "redstone_dust", "flower_pot"]
SOUND_TYPE_ALLOWANCES9 = [8, 9, 10, 11, 25, 26, 30, 36, 55, 97, 116, 117, 118, 119, 131, 132, 137, 138, 140] # all numbers since they can have the same ids now
SOUND_TYPE_ALLOWANCES10 = [8, 9, 10, 11, 25, 26, 30, 36, 55, 97, 116, 117, 118, 119, 131, 132, 137, 138, 140, 145] # 145 is anvil
SOUND_TYPE_ALLOWANCES11 = [8, 9, 10, 11, 25, 26, 30, 36, 55, 97, 115, 116, 117, 118, 119, 131, 132, 137, 138, 140, 145] # 115 is netherStalk
SOUND_TYPE_ALLOWANCES12 = [8, 9, 10, 11, 53, 55]
SOUND_TYPE_ALLOWANCES13 = [8, 9, 10, 11]
SOUND_TYPE_SHUT_UP1 = ["slime", "barrier"]
SOUND_TYPE_SHUT_UP2 = ["minecraft:slime", "minecraft:barrier"] # all of them for a few snapshots have "minecraft:" for some reason
SOUND_TYPES_CONDENSED1 = {"wood": "wood", "gravel": "gravel", "grass": "grass", "1.0 1.0 dig.stone step.stone dig.stone": "stone", "1.0 1.5 dig.stone step.stone dig.stone": "metal","1.0 1.0 dig.glass step.stone step.stone": "glass","cloth": "cloth", "sand": "sand", "snow": "snow", "1.0 1.0 dig.wood step.ladder dig.wood": "ladder", "0.3 1.0 dig.stone step.anvil random.anvil_land": "anvil", "1.0 1.0 mob.slime.big mob.slime.small mob.slime.big": "slime"}
SOUND_TYPES_CONDENSED2 = {"wood": "wood", "gravel": "gravel", "grass": "grass", "1.0 1.0 dig.stone step.stone dig.stone": "stone", "1.0 1.5 dig.stone step.stone dig.stone": "metal","1.0 1.0 random.glass step.stone step.stone": "glass","cloth": "cloth", "sand": "sand", "snow": "snow", "1.0 1.0 dig.wood step.ladder dig.wood": "ladder", "0.3 1.0 dig.stone step.anvil random.anvil_land": "anvil", "1.0 1.0 mob.slime.big mob.slime.small mob.slime.big": "slime"}


dataminers:list[DataMiner.DataMiner] = [
    BlocksNew.BlocksNew("19w36a", "-"),
    Blocks1.Blocks1("1.14_combat-0", "19w35a"),
    BlocksNew.BlocksNew("1.14.4", "1.14.4"),
    Blocks1.Blocks1("18w43a", "1.14.4-pre7"),
    Blocks2.Blocks2("17w50a", "1.13.2"      , record_start_threshold=3),
    Blocks2.Blocks2("17w47a", "17w49b"      , record_start_threshold=2), # post-flattening
    Blocks3.Blocks3("15w49b", "17w46a"      ), # pre-flattening
    Blocks4.Blocks4("1.8.9", "1.8.9", blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES2, sound_type_allowances=SOUND_TYPE_ALLOWANCES1), # pre-subtitles renaming & sound type code restructuring
    Blocks3.Blocks3("15w43a", "15w49a"      ),
    Blocks4.Blocks4("15w31a", "15w42a"      , blocks_list_record_threshold=2, sound_type_overrides=SOUND_TYPE_OVERRIDES1, sound_type_allowances=SOUND_TYPE_ALLOWANCES1),
    Blocks4.Blocks4("1.8.2-pre5", "1.8.8"   , blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES2, sound_type_allowances=SOUND_TYPE_ALLOWANCES1),
    Blocks4.Blocks4("14w33a", "1.8.2-pre4"  , blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES2, sound_type_allowances=SOUND_TYPE_ALLOWANCES1, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("14w32c", "14w32d"      , blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES2, sound_type_allowances=SOUND_TYPE_ALLOWANCES2, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("14w32a", "14w32b"      , blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES2, sound_type_allowances=SOUND_TYPE_ALLOWANCES3, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("14w31a", "14w31a"      , blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES3, sound_type_allowances=SOUND_TYPE_ALLOWANCES3, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("14w27a", "14w30c"      , blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES3, sound_type_allowances=SOUND_TYPE_ALLOWANCES4, sound_type_class_name_getter_mode=1), # idc i don't wanna rework the darn thing again
    Blocks4.Blocks4("14w20a", "14w26c"      , next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES3, sound_type_allowances=SOUND_TYPE_ALLOWANCES4, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("1.7.10-pre1", "1.7.10" , search_mode=1, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES3, sound_type_allowances=SOUND_TYPE_ALLOWANCES5, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("14w11b", "14w19a"      , search_mode=0, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES3, sound_type_allowances=SOUND_TYPE_ALLOWANCES4, sound_type_class_name_getter_mode=1), # why does it keep switching im dying. Its allowances go back a version too? whyyy?
    Blocks4.Blocks4("1.7", "1.7.9"            , next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES3, sound_type_allowances=SOUND_TYPE_ALLOWANCES5, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1), # removed the search mode thing with a try except statement in Blocks4 # alright i "fixed" it
    Blocks4.Blocks4("13w42a", "13w43a"            , next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES4, sound_type_allowances=SOUND_TYPE_ALLOWANCES5, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("13w41b", "13w41b"            , sound_types_condensed=SOUND_TYPES_CONDENSED2, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES4, sound_type_allowances=SOUND_TYPE_ALLOWANCES5, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("13w41a", "13w41a"            , skip_blocks=["chest_locked_aprilfools_super_old_legacy_we_should_not_even_have_this"], sound_types_condensed=SOUND_TYPES_CONDENSED2, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES4, sound_type_allowances=SOUND_TYPE_ALLOWANCES5, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1), # block was actually removed in 13w41b apparently
    Blocks4.Blocks4("13w38b", "13w39b"            , sound_types_condensed=SOUND_TYPES_CONDENSED2, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES4, sound_type_allowances=SOUND_TYPE_ALLOWANCES5, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("13w38a", "13w38a"            , sound_types_condensed=SOUND_TYPES_CONDENSED2, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES4, sound_type_allowances=SOUND_TYPE_ALLOWANCES6, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1), # god fricking damnit I just noticed all the code names say "static". No it doesn't matter I'm not going back.
    Blocks5.Blocks5("1.6.4", "1.6.4", sound_type_allowances=SOUND_TYPE_ALLOWANCES8), # finally moved on
    Blocks4.Blocks4("13w37b", "13w37b"            , sound_types_condensed=SOUND_TYPES_CONDENSED2, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES4, sound_type_allowances=SOUND_TYPE_ALLOWANCES6, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1),
    Blocks5.Blocks5("1.6.3", "1.6.3", sound_type_allowances=SOUND_TYPE_ALLOWANCES8),
    Blocks4.Blocks4("13w37a", "13w37a"            , sound_types_condensed=SOUND_TYPES_CONDENSED2, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES4, sound_type_allowances=SOUND_TYPE_ALLOWANCES6, sound_type_shut_up=SOUND_TYPE_SHUT_UP1, sound_type_class_name_getter_mode=1),
    Blocks4.Blocks4("13w36a", "13w36b"            , sound_types_condensed=SOUND_TYPES_CONDENSED2, next_line_look_ahead=0, blocks_record_threshold=1, blocks_list_record_threshold=1, sound_type_overrides=SOUND_TYPE_OVERRIDES5, sound_type_allowances=SOUND_TYPE_ALLOWANCES7, sound_type_shut_up=SOUND_TYPE_SHUT_UP2, sound_type_class_name_getter_mode=1),
    Blocks5.Blocks5("13w24a", "1.6.2", sound_type_allowances=SOUND_TYPE_ALLOWANCES8),
    Blocks6.Blocks6("1.4", "13w23b", sound_type_allowances=SOUND_TYPE_ALLOWANCES9), # "new" function is removed, just old now. Also I don't want a repeat of Blocks4 so I'm making a new one now.
    Blocks6.Blocks6("12w34a", "12w42b", sound_type_allowances=SOUND_TYPE_ALLOWANCES10),
    Blocks6.Blocks6("12w07a", "1.3.2", sound_type_allowances=SOUND_TYPE_ALLOWANCES11),
    Blocks6.Blocks6("b1.2", "12w06a", sound_type_allowances=SOUND_TYPE_ALLOWANCES11, magic_number=256),
    Blocks6.Blocks6("b1.0", "b1.1_02", sound_type_allowances=SOUND_TYPE_ALLOWANCES11, magic_number=256, search_mode=1),
    Blocks7.Blocks7("inf-20100630-1", "a1.2.6", sound_type_allowances=SOUND_TYPE_ALLOWANCES12),
    Blocks8.Blocks8("in-20100125-1", "inf-20100629", sound_type_allowances=SOUND_TYPE_ALLOWANCES13),
    NoneDataMiner.NoneDataMiner("in-20100111-1", "in-20100111-1"),
    Blocks9.Blocks9("in-20100105", "in-20100105", sound_type_allowances=SOUND_TYPE_ALLOWANCES13), # very short because sound was disabled around this time # I just wrote a whole dataminer from scratch just for it to last one version; fuck # remember to check that the code you're writing is useful, I guess.
    # I'm not writing another one; there's only like ten versions left
    NoneDataMiner.NoneDataMiner("-", "in-20091231-2")
]

Blocks = DataMinerType.DataMinerType("blocks.json", dataminers)

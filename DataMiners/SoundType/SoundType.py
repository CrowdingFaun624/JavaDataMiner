import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.SoundType.SoundTypeNew as SoundTypeNew
import DataMiners.SoundType.SoundType1 as SoundType1
import DataMiners.SoundType.SoundType2 as SoundType2
import DataMiners.SoundType.SoundType3 as SoundType3
import DataMiners.SoundType.SoundType4 as SoundType4
import DataMiners.SoundType.SoundType5 as SoundType5
import DataMiners.SoundType.SoundType6 as SoundType6
import DataMiners.SoundType.SoundType7 as SoundType7
import DataMiners.SoundType.SoundType8 as SoundType8
import DataMiners.SoundType.SoundType9 as SoundType9

dataminers:list[DataMiner.DataMiner] = [
    SoundTypeNew.SoundTypeNew("19w36a", "-"),
    SoundType1.SoundType1("1.14_combat-0", "19w35a"),
    SoundTypeNew.SoundTypeNew("1.14.4", "1.14.4"),
    SoundType1.SoundType1("15w49b", "1.14.4-pre7"),
    SoundType2.SoundType2("1.8.9", "1.8.9", ignore_sound_events=["step.anvil"]), # sound types begin being included in Blocks.java; MC-7849
    SoundType1.SoundType1("15w43a", "15w49a"),
    SoundType2.SoundType2("1.8.2-pre5", "15w42a", ignore_sound_events=["step.anvil"]),
    SoundType3.SoundType3("14w20a", "1.8.2-pre4", ignore_sound_events=["step.anvil"]),
    SoundType3.SoundType3("13w49a", "1.7.10", ignore_sound_events=["step.anvil"], search_mode=1),
    SoundType3.SoundType3("13w38a", "13w48b", search_mode=1, rely_on_sounds=False), # when sounds become neutral evil
    SoundType3.SoundType3("1.6.4", "1.6.4", search_mode=2, rely_on_sounds=False),
    SoundType3.SoundType3("13w37b", "13w37b", search_mode=1, rely_on_sounds=False),
    SoundType3.SoundType3("1.6.3", "1.6.3", search_mode=2, rely_on_sounds=False),
    SoundType3.SoundType3("13w36a", "13w37a", search_mode=1, rely_on_sounds=False),
    SoundType3.SoundType3("12w39a", "1.6.2", search_mode=2, rely_on_sounds=False),
    SoundType4.SoundType4("b1.2", "12w38b", rely_on_sounds=False),
    SoundType4.SoundType4("b1.0", "b1.1_02", search_mode=1, rely_on_sounds=False),
    SoundType5.SoundType5("inf-20100630-1", "a1.2.6"),
    SoundType6.SoundType6("inf-20100627", "inf-20100629", get_imports=False),
    SoundType6.SoundType6("in-20100212-1", "inf-20100625-2", get_imports=True), # code structure changed; now organized into folders
    SoundType7.SoundType7("in-20100125-1", "in-20100207-2"), # massive simplification to sound types, as they are now hard-coded to always be "step." + name
    SoundType9.SoundType9("in-20100111-1", "in-20100111-1"),
    SoundType8.SoundType8("in-20100105", "in-20100105"),
    SoundType9.SoundType9("c0.0.22a", "in-20091231-2"),
    NoneDataMiner.NoneDataMiner("-", "c0.0.21a_01"),
]

SoundType = DataMinerType.DataMinerType("sound_types.json", dataminers)

import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.Notes.NotesNew as NotesNew

dataminers:list[DataMiner.DataMiner] = [ # this thing is intended to help make SoundEvents pre-1.6 more accurate
    NoneDataMiner.NoneDataMiner("13w49a", "-"),
    NotesNew.NotesNew("b1.2", "13w48b"),
    NoneDataMiner.NoneDataMiner("-", "b1.1_02")
]

Notes = DataMinerType.DataMinerType("notes.json", dataminers)

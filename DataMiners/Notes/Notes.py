import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner

import DataMiners.Notes.NotesNew as NotesNew

dataminers:list[DataMiner.DataMiner] = [ # this thing is intended to help make SoundEvents pre-1.6 more accurate
    NotesNew.NotesNew("b1.2", "13w48b")
]

Notes = DataMinerType.DataMinerType("notes.json", dataminers)

import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.Subtitles.SubtitlesNew as SubtitlesNew

dataminers:list[DataMiner.DataMiner] = [
    SubtitlesNew.SubtitlesNew("15w43b", "-"),
    NoneDataMiner.NoneDataMiner("-", "15w43a")
]

Subtitles = DataMinerType.DataMinerType("subtitles.json", dataminers)

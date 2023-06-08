import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner

import DataMiners.Subtitles.SubtitlesNew as SubtitlesNew

dataminers:list[DataMiner.DataMiner] = [
    SubtitlesNew.SubtitlesNew("15w43b", "-")
]

Subtitles = DataMinerType.DataMinerType("subtitles.json", dataminers)

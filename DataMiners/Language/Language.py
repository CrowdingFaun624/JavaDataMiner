import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.Language.Language1 as Language1
import DataMiners.Language.LanguageNew as LanguageNew

dataminers:list[DataMiner.DataMiner] = [
    LanguageNew.LanguageNew("18w02a", "-"),
    Language1.Language1("b1.0", "18w01a"),
    NoneDataMiner.NoneDataMiner("-", "a1.2.6"),
]

Language = DataMinerType.DataMinerType("language.json", dataminers)

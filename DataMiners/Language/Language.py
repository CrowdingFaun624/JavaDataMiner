import DataMiners.DataMiner as DataMiner

import DataMiners.Language.Language1 as Language1
import DataMiners.Language.LanguageNew as LanguageNew

dataminers:list[DataMiner.DataMiner] = [
    Language1.Language1("b1.0", "18w01a"),
    LanguageNew.LanguageNew("18w02a", "-")
]

import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner

import DataMiners.Records.Records1 as Records1
import DataMiners.Records.RecordsNew as RecordsNew

dataminers:list[DataMiner.DataMiner] = [
    RecordsNew.RecordsNew("b1.9-pre2", "1.0.0-rc2-3"), # this upper bound is entirely arbitrary; I just don't want to unzip and datamine all ~717 versions after this.
    RecordsNew.RecordsNew("b1.0", "b1.9-pre1", search_terms=["cat", "13", "record"]), # rest of music discs are added
    Records1.Records1("a1.0.14", "a1.2.6")
]

Records = DataMinerType.DataMinerType("records.json", dataminers)
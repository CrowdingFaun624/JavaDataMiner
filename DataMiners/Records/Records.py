import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.Records.Records1 as Records1
import DataMiners.Records.Records0 as Records0

dataminers:list[DataMiner.DataMiner] = [
    NoneDataMiner.NoneDataMiner("13w49a", "-"),
    Records0.Records0("1.7.1", "13w48b", search_terms=["\"mellohi\""]),
    Records0.Records0("13w42a", "1.7", search_terms=["records.mellohi"]),
    Records0.Records0("11w47a", "13w41b", search_terms=["\"mellohi\""]),
    Records0.Records0("b1.9-pre2", "1.0"),
    Records0.Records0("b1.0", "b1.9-pre1", search_terms=["cat", "13", "record"]), # rest of music discs are added
    Records1.Records1("a1.0.14", "a1.2.6"),
    NoneDataMiner.NoneDataMiner("-", "a1.0.13_01-2")
]

Records = DataMinerType.DataMinerType("records.json", dataminers)
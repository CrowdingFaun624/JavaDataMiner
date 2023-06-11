import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner

import DataMiners.LiteralStrings.LiteralStringsNew as LiteralStringsNew

dataminers:list[DataMiner.DataMiner] = [
    LiteralStringsNew.LiteralStringsNew("-", "13w49a") # one version into lawful good for extra juicy comparison
]

LiteralStrings = DataMinerType.DataMinerType("literal_strings.json", dataminers)

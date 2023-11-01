from typing import Any

import DataMiners.DataMiner as DataMiner

class NoneDataMiner(DataMiner.DataMiner):
    def activate(self, version:str, store:bool=True, return_value:Any|None=None, **kwargs) -> None:
        return return_value

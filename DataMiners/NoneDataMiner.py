import DataMiners.DataMiner as DataMiner

class NoneDataMiner(DataMiner.DataMiner):
    def activate(self, version:str, store:bool=True, **kwargs) -> None:
        return None

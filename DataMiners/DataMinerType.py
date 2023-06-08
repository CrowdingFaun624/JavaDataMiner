import DataMiners.DataMiner as DataMiner

class DataMinerType():
    def __init__(self, file_name:str, dataminers:list[DataMiner.DataMiner]) -> None:
        self.file_name = file_name
        self.dataminers = dataminers

    def get_data_file(self, version:str, kwargs:dict[str,any]|None=None, redo:bool=False) -> any:
        '''Returns the data file for this version, creating it if it does not exist.'''
        return DataMiner.get_data_file(version, self.file_name, self.dataminers, redo, kwargs)

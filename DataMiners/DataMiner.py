import json
import os

import Importer.Manifest as Manifest

class DataMiner():
    def __init__(self, start_version:str, end_version:str) -> None:
        self.start_version = start_version
        if start_version == "-": start_version = Manifest.get_id_version(0)
        self.start_id = Manifest.get_version_id(start_version)
        self.end_version = end_version
        if end_version == "-": end_version = Manifest.get_latest()[1]
        self.end_id = Manifest.get_version_id(end_version)
    
    def is_valid_version(self, version:str) -> bool:
        '''Returns if the given version is within the dataminer's range.'''
        version_id = Manifest.get_version_id(version)
        return version_id >= self.start_id and version_id <= self.end_id

    def activate(self, version:str) -> any: ...

    def sort_dict(input_dict:dict) -> dict:
        '''Sorts a dict by its keys, then values'''
        output = [(k, v) for k, v in input_dict.items()]
        output = sorted(output)
        output = dict(output)
        return output

    def store(self, version:str, data:any, file_name:str) -> None:
        if not os.path.exists("./_versions/%s/data" % version): os.mkdir("./_versions/%s/data" % version)
        if isinstance(data, str): write_data = data
        else: write_data = json.dumps(data, indent=2)
        with open("./_versions/%s/data/%s" % (version, file_name), "wt") as f:
            f.write(write_data)

def get_dataminer(version:str, dataminer_list:list[DataMiner]) -> DataMiner|None:
    '''Takes a version and a list of dataminers from DataMiners.py. Returns a dataminer that will work on the version, or None'''
    for dataminer in dataminer_list:
        if dataminer.is_valid_version(version): return dataminer
    else: return None

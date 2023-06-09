import json
import os

import Importer.Manifest as Manifest

class DataMiner():
    def __init__(self, start_version:str, end_version:str, **kwargs) -> None:
        self.start_version = start_version
        if start_version == "-": start_version = Manifest.get_id_version(0)
        self.start_id = Manifest.get_version_id(start_version)
        self.end_version = end_version
        if end_version == "-": end_version = Manifest.get_latest()[1]
        self.end_id = Manifest.get_version_id(end_version)
        if kwargs is None: kwargs = {}
        self.init(**kwargs)
    
    def is_valid_version(self, version:str) -> bool:
        '''Returns if the given version is within the dataminer's range.'''
        version_id = Manifest.get_version_id(version)
        return version_id >= self.start_id and version_id <= self.end_id

    def search(self, version:str) -> str: ...

    def activate(self, version:str, store:bool=True, **kwargs) -> any: ...

    def init(self, **kwargs) -> None: ... # for other variables declared upon the declaration of the dataminer.

    def sort_dict(input_dict:dict, by_values:bool=False) -> dict:
        '''Sorts a dict by its keys, then values'''
        if by_values: output = [(v, k) for k, v in input_dict.items()]
        else: output = [(k, v) for k, v in input_dict.items()]
        output = sorted(output)
        if by_values: output = [(v, k) for k, v in output]
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

def get_file_name_from_path(file_path:str) -> str:
    return ".".join(os.path.split(file_path)[1].split(".")[:-1])

def get_data_file(version:str, file_name:str, dataminer_list:list[DataMiner], redo:bool=False, kwargs:dict[str,any]|None=None) -> any:
    '''Returns the specified data file for this version, creating it if it does not exist or `redo` is True.'''
    file_path = os.path.join("./_versions", version, "data", file_name)
    if os.path.exists(file_path) and not redo:
        with open(file_path, "rt") as f:
            return json.loads(f.read())
    else:
        dataminer = get_dataminer(version, dataminer_list)
        if dataminer is None: return None
        if kwargs == {} or kwargs is None:
            return dataminer.activate(version)
        else:
            return dataminer.activate(version, kwargs=kwargs)

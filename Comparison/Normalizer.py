from typing import TypeVar

import Importer.Manifest as Manifest

ACTIVATE_DATA = TypeVar("ACTIVATE_DATA")

class Normalizer():
    def __init__(self, start_version:str, end_version:str, **kwargs) -> None:
        self.start_version = start_version
        if start_version == "-": start_version = Manifest.get_id_version(0); self.is_earliest = True
        else: self.is_earliest = False
        self.start_id = Manifest.get_version_id(start_version)
        self.end_version = end_version
        if end_version == "-": end_version = Manifest.get_latest()[1]; self.is_latest = True
        else: self.is_latest = False
        self.end_id = Manifest.get_version_id(end_version)
        if kwargs is None: kwargs = {}
        self.init(**kwargs)

    def init(self, **kwargs) -> None: ...

    def activate(self, data:ACTIVATE_DATA, version:str, suppress_domain_errors:bool=False) -> ACTIVATE_DATA: ...
    
    def is_valid_version(self, version:str) -> bool:
        '''Returns if the given version is within the dataminer's range.'''
        if version == "-": return self.is_earliest # stand-in for before oldest version.
        version_id = Manifest.get_version_id(version)
        return version_id >= self.start_id and version_id <= self.end_id

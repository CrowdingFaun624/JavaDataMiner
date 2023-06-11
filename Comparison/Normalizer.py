import Importer.Manifest as Manifest

class Normalizer():
    def __init__(self, start_version:str, end_version:str, **kwargs) -> None:
        self.start_version = start_version
        if start_version == "-": start_version = Manifest.get_id_version(0)
        self.start_id = Manifest.get_version_id(start_version)
        self.end_version = end_version
        if end_version == "-": end_version = Manifest.get_latest()[1]
        self.end_id = Manifest.get_version_id(end_version)
        if kwargs is None: kwargs = {}
        self.init(**kwargs)

    def init(self, **kwargs) -> None: ...

    def activate(self, data:any, version:str) -> any: ...
    
    def is_valid_version(self, version:str) -> bool:
        '''Returns if the given version is within the dataminer's range.'''
        version_id = Manifest.get_version_id(version)
        return version_id >= self.start_id and version_id <= self.end_id

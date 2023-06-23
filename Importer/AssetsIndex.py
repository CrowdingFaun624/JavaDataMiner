'''Gets the versions assets index file.'''

import json
import os

import Importer.VersionJson as VersionJson
import Importer.WebRequest as WebRequest

def fetch_assets_index(version:str, version_json:dict=None, store:bool=True, store_in_version:bool=False) -> dict[str,dict[str,dict[str|int]]]:
    '''Returns the assets index as a dict. Set `store` to True to place the fancified assets index in ./assets as <id>.json.'''
    if version_json is None: version_json = VersionJson.get_version_json(version)
    if "assetIndex" not in version_json: raise KeyError(f"Version {version} has no assets index!")
    assets_id = version_json["assetIndex"]["id"]
    url = version_json["assetIndex"]["url"]
    assets_index = WebRequest.web_request(url, "j")
    if store:
        with open("./_assets/indexes/%s.json" % assets_id, "wt") as f:
            f.write(json.dumps(assets_index, indent=2))
    if store_in_version:
        with open("./_versions/%s/assets.json" % version, "wt") as f:
            f.write(json.dumps(assets_index, indent=2))
    return assets_index

def get_assets_index(id:str, version:str=None) -> dict[str,dict[str,dict[str|int]]]:
    '''Returns the assets index using the version, first from file, then from url if that doesn't work.'''
    if os.path.exists("./_assets/indexes/%s.json" % id):
        with open("./_assets/indexes/%s.json" % id, "rt") as f:
            return json.loads(f.read())
    else:
        if version is None: raise FileNotFoundError("Unable to find asset index %s when no version is provided!" % id)
        return fetch_assets_index(version, store=True)

def get_assets_in_folder(folder:str, id:str=None, version:str=None, assets_index:dict=None) -> list[str]:
    '''Returns a list of items that start with the given string. Returned items include the given string at the start.'''
    if assets_index is None: assets_index = get_assets_index(id, version)
    output = [object for object in list(assets_index["objects"].keys()) if object.startswith(folder)]
    return output

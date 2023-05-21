import json
import os

import Importer.Manifest as Manifest
import Importer.WebRequest as WebRequest

def fetch_version_json(version:str, manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None, store:bool=False) -> dict:
    '''Returns the version.json as a dict. Set `store` to True to place the fancified manifest in ./versions/<version> as version.json.
    If `manifest` is None, then it will attempt to get the manifest from the file.'''
    def insert_client_url(version_json:dict, client_url:str) -> dict:
        if "downloads" not in version_json:
            version_json["downloads"] = {}
        if "client" not in version_json["downloads"]:
            version_json["downloads"]["client"] = {}
        version_json["downloads"]["client"]["url"] = client_url
        return version_json
    if manifest is None: manifest = Manifest.get_manifest()
    version_properties = Manifest.get_version(version, manifest)
    url:str = version_properties["url"]
    if url.startswith("http"):
        version_json:dict = WebRequest.web_request(url, "j")
    else:
        with open(url, "rt") as f:
            version_json = json.loads(f.read())
    if "clientUrl" in version_properties:
        client_url = version_properties["clientUrl"]
        version_json = insert_client_url(version_json, client_url)
    if store:
        if not os.path.exists("./_versions/%s" % version):
            os.mkdir("./_versions/%s" % version)
        with open("./_versions/%s/version.json" % version, "wt") as f:
            f.write(json.dumps(version_json, indent=2))
    assert isinstance(version_json, dict)
    return version_json

def get_version_json(version:str) -> dict:
    '''Returns the version.json as a dict. Will first try to get it from the file, then from the url.'''
    if os.path.exists("./_versions/%s/version.json" % version):
        with open("./_versions/%s/version.json" % version, "rt") as f:
            return json.loads(f.read())
    else: return fetch_version_json(version, store=True)

def get_asset_index(version:str) -> str:
    '''Returns the asset index.'''
    return get_version_json(version)["assetIndex"]["id"]

import datetime
import json
import os
import random

import Importer.WebRequest as WebRequest


def fetch_manifest(store:bool=False) -> dict[str,dict[str,str]|list[dict[str,str|int]]]:
    '''Returns the version manifest as a dict. Set `store` to True to place the fancified manifest in ./versions as version_manifest.json.'''
    manifest = WebRequest.web_request("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json", "j")
    manifest_latest = manifest["latest"]
    manifest_list = manifest["versions"]
    manifest_list = combine_manifests(manifest_list, get_manifest_extension())
    manifest = {"latest": manifest_latest, "versions": manifest_list}
    if store:
        with open("./_versions/version_manifest.json", "wt") as f:
            f.write(json.dumps(manifest, indent=2))
    return manifest

def get_manifest_from_file() -> dict[str,dict[str,str]|list[dict[str,str|int]]]:
    '''Returns the manifest, first from file, then from url if that doesn't work'''
    if os.path.exists("./_versions/version_manifest.json"):
        with open("./_versions/version_manifest.json", "rt") as f:
            return json.loads(f.read())
    else: return fetch_manifest(store=True)

def get_manifest_extension() -> list[dict[str,str|int]]:
    '''Returns the manifest extension of versions not in the launcher.'''
    with open("./Assets/manifest_extension.json", "rt") as f:
        return json.loads(f.read())

def combine_manifests(manifest1:list[dict[str,str|int]], manifest2:list[dict[str,str|int]]) -> list[dict[str,str|int]]:
    '''Takes two lists of dicts of version parameters and merges them and sorts them by releasetime.'''
    def sortkey(value) -> datetime.datetime:
        date = value["releaseTime"]
        if date[-6] in "+-" and ":" in date: date = date[:-6]
        return datetime.datetime.fromisoformat(date)
    manifest = manifest1.copy()
    manifest.extend(manifest2)
    manifest = sorted(manifest, key=sortkey, reverse=True)
    for version in manifest2:
        version_id = version["id"]
        for version2 in manifest:
            if version2["id"] == version_id: break
        else: raise KeyError("Version %s does not exist in combined manifest!" % version_id)
    return manifest

def get_version(version:str, manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None) -> dict[str,str|int]:
    '''Returns the version's properties from the manifest. If `manifest` is None, then it will attempt to get the manifest from the file.'''
    if manifest is None: manifest = get_manifest()
    for version_properties in manifest["versions"]:
        if version_properties["id"] == version: return version_properties
    else: raise KeyError("Version %s does not exist in the version manifest!" % version)

def get_latest(manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None) -> tuple[str,str]:
    '''Returns the latest release and latest snapshot. If `manifest` is None, then it will attempt to get the manifest from the file.'''
    if manifest is None: manifest = get_manifest()
    return manifest["latest"]["release"], manifest["latest"]["snapshot"]

def get_random_version(manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None) -> dict[str,str|int]:
    '''Returns a random version's properties from the manifest. If `manifest` is None, then it will attempt to get the manifest from the file.'''
    if manifest is None: manifest = get_manifest()
    return random.choice(manifest["versions"])

def get_version_id(version:str, manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None) -> int:
    '''Returns a unique, possibly occasionally changing id of a version. If `manifest` is None, then it will attempt to get the manifest from the file. The oldest  version is 0.'''
    if manifest is None: manifest = get_manifest()
    for index, version_properties in enumerate(reversed(manifest["versions"])):
        if version_properties["id"] == version:
            return index
    else: raise KeyError("Version {} does not exist in the version manifest!".format(version))

def get_id_version(id:int, manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None) -> str:
    '''Returns the id's version name. If `manifest` is None, then it will attempt to get the manifest from the file. The oldest version is 0.'''
    if manifest is None: manifest = get_manifest()
    return list(reversed(manifest["versions"]))[id]["id"]

def get_version_list(manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None) -> list[str]:
    '''Returns a list of versions, in order from newest to oldest. If `manifest` is None, then it will attempt to get the manifest from the file.'''
    if manifest is None: manifest = get_manifest()
    output = []
    for version in manifest["versions"]:
        output.append(version["id"])
    return output

manifest = get_manifest_from_file()

def get_manifest() -> dict[str,dict[str,str]|list[dict[str,str|int]]]:
    return manifest
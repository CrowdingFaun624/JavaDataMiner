import datetime
import json
import os
import random

import Importer.WebRequest as WebRequest

#TODO: fix weird bug affecting releaseTime
def fetch_manifest(store:bool=False) -> dict[str,dict[str,str]|list[dict[str,str|int]]]:
    '''Returns the version manifest as a dict. Set `store` to True to place the fancified manifest in ./versions as version_manifest.json.'''
    manifest = WebRequest.web_request("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json", "j")
    manifest_latest = manifest["latest"]
    manifest_list = manifest["versions"]
    version_order = list(reversed(get_version_order()))
    manifest_list = combine_manifests(manifest_list, get_manifest_extension(), version_order)
    manifest = {"latest": manifest_latest, "versions": manifest_list}
    if store:
        with open("./_versions/version_manifest.json", "wt") as f:
            f.write(json.dumps(manifest, indent=2))
    verify_information()
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

def combine_manifests(manifest1:list[dict[str,str|int]], manifest2:list[dict[str,str|int]], version_order:list[str]) -> list[dict[str,str|int]]:
    '''Takes two lists of dicts of version parameters and merges them and sorts them by the order file.'''
    def has_version(manifest:list[dict[str,str|int]], selected_version:str) -> bool:
        for version_properties in manifest:
            if version_properties["id"] == selected_version: return True
        else: return False
    def remove_version(manifest:list[dict[str,str|int]], version:str) -> list[dict[str,str|int]]:
        for index, version_properties in enumerate(manifest):
            if version_properties["id"] == version:
                del manifest[index]
                return manifest
        else: raise KeyError("Unable to find version \"%s\" in manifest!" % version)
    def special_extend(manifest:list[dict[str,str|int]], manifest2:list[dict[str,str|int]]) -> list[dict[str,str|int]]:
        for version_properties in manifest2:
            if has_version(manifest, version_properties["id"]):
                manifest = remove_version(manifest, version_properties["id"])
            manifest.append(version_properties)
        return manifest
    def special_sort(manifest:list[dict[str,str|int]], version_orders:list[str]) -> list[dict[str,str|int]]:
        '''Sorts the manifest.'''
        output:list[dict[str,str|int]] = []
        for version_order in version_orders:
            for version in manifest:
                if version["id"] == version_order:
                    output.append(version)
                    break
        return output
    manifest = manifest1.copy()
    manifest = special_extend(manifest, manifest2)
    manifest = special_sort(manifest, version_order)
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

def get_version_list(manifest:dict[str,dict[str,str]|list[dict[str,str|int]]]=None, reverse:bool=False) -> list[str]:
    '''Returns a list of versions, in order from newest to oldest. If `manifest` is None, then it will attempt to get the manifest from the file.'''
    if manifest is None: manifest = get_manifest()
    output = []
    for version in manifest["versions"]:
        output.append(version["id"])
    if reverse: return list(reversed(output))
    else: return output

def get_version_order() -> list[str]:
    '''Returns the order of all versions, including missing ones (oldest to newest).'''
    with open("./Assets/version_order.json", "rt") as f:
        return json.loads(f.read())

def get_missing_versions() -> list[str]:
    '''Returns the list of all unarchived versions (oldest to newest).'''
    with open("./Assets/missing_versions.json", "rt") as f:
        return json.loads(f.read())

def add_latest_to_version_order(version:str) -> None:
    '''Adds the latest version to version_order.json'''
    with open("./Assets/version_order.json", "rt") as f:
        order:list[str] = json.loads(f.read())
    if version in order: return
    manifest = get_version_list()
    if len(manifest) - len(order) != 1:
        print("Multiple versions detected! Please configure version_order.json.")
    order.append(version)
    with open("./Assets/version_order.json", "wt") as f:
        f.write(json.dumps(order, indent=2))
    print("Added \"%s\" to version order." % version)

def verify_information() -> None:
    '''Looks at the version manifest, the version order, and the missing versions to look for inconsistencies.'''
    manifest = get_manifest_from_file()
    version_manifests = get_version_list(manifest)
    version_orders = get_version_order()
    version_missings = get_missing_versions()
    is_bad = False
    for version_order in version_orders:
        if version_order not in version_manifests and version_order not in version_missings:
            print(f"version order \"{version_order}\" is in neither the version manifests nor the version missings!")
            is_bad = True
    for version_manifest in version_manifests:
        if version_manifest not in version_orders:
            print(f"version manifest \"{version_manifest}\" is not in the version orders!")
            is_bad = True
    for version_missing in version_missings:
        if version_missing not in version_orders:
            print(f"version missing \"{version_missing}\" is not in the version orders!")
            is_bad = True
    for version_missing in version_missings:
        if version_missing in version_manifests:
            print(f"version missing \"{version_missing}\" is in the version manifests")
            is_bad = True
    if is_bad: raise KeyError("Failed to verify manifest informations!")

manifest = get_manifest_from_file()

def get_manifest() -> dict[str,dict[str,str]|list[dict[str,str|int]]]:
    '''Returns the manifest'''
    return manifest

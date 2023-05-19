import json
import os

import Importer.AssetImporter as AssetImporter
import Importer.AssetsIndex as AssetsIndex
import Importer.Manifest as Manifest
import Importer.VersionJson as VersionJson

# def reconstruct(current_version:str, manifest:dict=None) -> None:
#     def is_same(asset:bytes, name:str) -> bool:
#         '''Returns True if the asset is the same from the one already stored, False if it is
#         different or does not exist.'''
#         previous_asset = get_asset(name, current_version, previous_versions, error=False)
#         if previous_asset is None: return False
#         else: return asset == previous_asset
#     if manifest is None: manifest = Manifest.get_manifest()
#     previous_versions = get_previous_versions(current_version, manifest)
#     # asset_index_id = VersionJson.get_asset_index(current_version)
#     asset_index = AssetsIndex.fetch_assets_index(current_version, store=True, store_in_version=True)
#     for name, data in list(asset_index["objects"].items()):
#         print(name)
#         asset:bytes = AssetImporter.fetch_asset_from_hash(data["hash"], "b")
#         if not is_same(asset, name):
#             path = os.path.join("./_assets_storage", current_version, name)
#             folder_path = os.path.split(path)[0]
#             if not os.path.exists(folder_path): os.makedirs(folder_path, exist_ok=True)
#             with open(path, "wb") as f:
#                 f.write(asset)
#     with open(os.path.join("./_assets_storage", current_version, "index.json"), "wt") as f:
#         f.write(json.dumps(asset_index, indent=2))

# def get_asset(name:str, current_version:str, previous_versions:list[str]=None, error:bool=True) -> bytes|None:
#     '''Gets the asset from the latest version. If `error` is True, then it will return a FileNotFoundError upon no file found'''
#     if previous_versions is None: previous_versions = get_previous_versions(current_version)
#     for version_name in previous_versions:
#         path = os.path.join("./_assets_storage", version_name, name)
#         if os.path.exists(path):
#             with open(path, "rb") as f:
#                 content = f.read()
#             return content
#     else:
#         if error: raise FileNotFoundError("Asset {} was not found before {}!".format(name, current_version))
#         else: return None

def get_previous_versions(current_version:str, manifest:dict=None) -> list[str]:
    '''Gets the previous versions that was archived in ./_assets_storage from latest to oldest'''
    if manifest is None: manifest = Manifest.get_manifest()
    versions = get_stored_versions()
    version_ids = [Manifest.get_version_id(version, manifest) for version in versions]
    current_version_id = Manifest.get_version_id(current_version, manifest)
    version_ids_lower = [version_id for version_id in version_ids if version_id < current_version_id]
    version_ids = sorted(version_ids_lower, reverse=True)
    version_names = [Manifest.get_id_version(version_id, manifest) for version_id in version_ids]
    return version_names

def get_indexes(new_version:str, manifest:dict=None) -> list[dict[str,dict[str,str|int]]]:
    '''Gets the objects of the indexes from the last stored version and the new version'''
    if manifest is None: manifest = Manifest.get_manifest()
    old_version = get_previous_versions(new_version, manifest)[0]
    new_index = AssetsIndex.fetch_assets_index(new_version, store=True)
    with open(os.path.join("./_assets_storage", old_version, "index.json"), "rt") as f:
        old_index = json.loads(f.read())
    return [old_index["objects"], new_index["objects"]]

def get_added_or_removed(index1:dict[str,dict[str,str|int]], index2:dict[str,dict[str,str|int]]) -> list[str]:
    '''Returns items that are in index1 that aren't in index2'''
    output:list[str] = []
    for name in list(index1.keys()):
        if name not in index2:
            output.append(name)
    return output

def get_changed(old_index:dict[str,dict[str,str|int]], new_index:dict[str,dict[str,str|int]]) -> list[str]:
    '''Returns a list of names that have exist on both sides and have differing hashes or sizes'''
    new_index_names = set(list(new_index.keys()))
    output:list[str] = []
    for name, old_content in list(old_index.items()):
        if name not in new_index_names: continue
        new_content = new_index[name]
        if old_content != new_content:
            output.append(name)
    return output

def get_added(old_index:dict[str,dict[str,str|int]], new_index:dict[str,dict[str,str|int]]) -> list[str]:
    return get_added_or_removed(new_index, old_index)
def get_removed(old_index:dict[str,dict[str,str|int]], new_index:dict[str,dict[str,str|int]]) -> list[str]:
    return get_added_or_removed(old_index, new_index)

def get_all_changes(old_index:dict[str,dict[str,str|int]], new_index:dict[str,dict[str,str|int]]) -> list[list[str], list[str], list[str]]:
    '''Returns all added items, all removed items, and all changed items'''
    return (get_added(old_index, new_index), get_removed(old_index, new_index), get_changed(old_index, new_index))

def reconstruct(new_version:str, manifest:dict=None) -> None:
    if manifest is None: manifest = Manifest.get_manifest()
    indexes = get_indexes(new_version, manifest)
    old_index, new_index = indexes[0], indexes[1]
    store_index(new_version, new_index)
    changes = get_all_changes(old_index, new_index)
    write_changelog(new_version, old_index=old_index, new_index=new_index, changes=changes)
    download_items = changes[0] + changes[2] # added + changed
    for name in download_items:
        object_hash = new_index[name]["hash"]
        asset_bytes:bytes = AssetImporter.fetch_asset_from_hash(object_hash, "b")
        folder_path = os.path.split(name)[0]
        os.makedirs(os.path.join("./_assets_storage", new_version, folder_path), exist_ok=True)
        with open(os.path.join("./_assets_storage", new_version, name), "wb") as f:
            f.write(asset_bytes)

def make_changelog(old_index:dict[str,dict[str,str|int]], new_index:dict[str,dict[str,str|int]], changes:list[list[str]]=None) -> str:
    ADDED_TITLE = "Additions:\n"
    REMOVED_TITLE = "Removals:\n"
    CHANGED_TITLE = "Changed:\n"
    ADDED_ELEMENT = "\tAdded \"%s\"\n"
    REMOVED_ELEMENT = "\tRemoved \"%s\"\n"
    CHANGED_ELEMENT = "\tChanged \"%s\"\n"
    if changes is None: added, removed, changed = get_all_changes(old_index, new_index)
    else: added, removed, changed = changes
    output = ""
    if len(added) > 0: output += ADDED_TITLE
    for addition in added:
        output += ADDED_ELEMENT % addition
    if len(removed) > 0: output += REMOVED_TITLE
    for removal in removed:
        output += REMOVED_ELEMENT  % removal
    if len(changed) > 0: output += CHANGED_TITLE
    for change in changed:
        output += CHANGED_ELEMENT % change
    return output

def write_changelog(version:str, changelog:str|None=None, old_index:dict[str,dict[str,str|int]]|None=None, new_index:dict[str,dict[str,str|int]]|None=None, changes:list[list[str]]|None=None) -> None:
    '''Writes the given changelog to a file or finds the changelog itself'''
    if changelog is None:
        if old_index is None or new_index is None:
            raise ValueError("An index is not specified!")
        changelog = make_changelog(old_index, new_index, changes=changes)
    with open(os.path.join("./_assets_storage", version, "changelog.txt"), "wt") as f:
        f.write(changelog)

def store_index(version:str, index:dict) -> None:
    if not os.path.exists(os.path.join("./_assets_storage", version)):
        os.mkdir(os.path.join("./_assets_storage", version))
    with open(os.path.join("./_assets_storage", version, "index.json"), "wt") as f:
        f.write(json.dumps({"objects": index}, indent=2))

def get_stored_versions() -> list[str]:
    folders = os.listdir("./_assets_storage")
    return folders
# TODO: add changelog maker
def main() -> None:
    manifest = Manifest.get_manifest()
    current_version = Manifest.get_latest(manifest)[1] # latest snapshot
    reconstruct(current_version, manifest)

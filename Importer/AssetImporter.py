import json
import os

import Importer.AssetsIndex as AssetsIndex
import Importer.VersionJson as VersionJson
import Importer.WebRequest as WebRequest

ASSETS_URL = "https://resources.download.minecraft.net/%s/%s"

def fetch_asset(id:str, name:str, mode:str="t", version:str=None, store:bool=True, store_in_version:bool=False, assets_index:dict=None) -> str|bytes|dict:
    '''Fetches an asset with name `name` from `id`. `mode` can be "t" (text), "b" (bytes), or "j" (json)'''
    asset_hash = get_hash(id, name, assets_index, version=version)
    first_two_letters = asset_hash[:2]
    content = fetch_asset_from_hash(asset_hash, mode)
    if mode in ("t", "b"): write_content = content
    else: write_content = json.dumps(content, indent=2)
    write_mode = {"t": "t", "b": "b", "j": "t"}[mode]
    if store:
        if not os.path.exists("./_assets/objects/%s" % first_two_letters): os.mkdir("./_assets/objects/%s" % first_two_letters)
        with open("./_assets/objects/%s/%s" % (first_two_letters, asset_hash), "w"+write_mode) as f:
            f.write(write_content)
    if store_in_version:
        if version is None: raise ValueError("Attempted to store in version with no version name provided!")
        if not os.path.exists("./_versions/%s/assets" % version): os.mkdir("./_versions/%s/assets" % version)
        os.makedirs(os.path.split("./_versions/%s/assets/%s" % (version, name))[0], exist_ok=True)
        with open("./_versions/%s/assets/%s" % (version, name), "w"+write_mode) as f:
            f.write(write_content)
    return content

def fetch_asset_from_hash(asset_hash:str, mode:str="t") -> str|bytes|dict:
    '''Fetches an asset using the given hash. `mode` can be "t" (text), "b" (bytes), or "j" (json)'''
    first_two_letters = asset_hash[:2]
    return WebRequest.web_request(ASSETS_URL % (first_two_letters, asset_hash), mode)

def get_hash(id:str, name:str, assets_index:dict=None, version:str=None) -> str:
    '''Gets an object's hash using its asset index and name'''
    if assets_index is None: assets_index = AssetsIndex.get_assets_index(id, version)
    if name in assets_index["objects"]:
        hash = assets_index["objects"][name]["hash"]
        return hash
    else: raise KeyError("%s does not exist in %s!" % (name, id))

def get_hashes(id:str, names:list[str], assets_index:dict=None, version:str=None) -> dict[str,str]:
    '''Gets multiple objects' hashes using their asset indexes and names'''
    if assets_index is None: assets_index = AssetsIndex.get_assets_index(id, version)
    output = {}
    for name in names:
        output[name] = get_hash(id, name, assets_index)
    return output

def get_asset(id:str, name:str, mode:str="t", hash:str=None) -> str|bytes|dict:
    '''Gets an asset from its id and name. `mode` can be "t" (text), "b" (bytes), or "j" (json)'''
    if hash is None: hash = get_hash(id, name)
    first_two_letters = hash[:2]
    if os.path.exists("./_assets/objects/%s/%s" % (first_two_letters, hash)):
        write_mode = {"t": "t", "b": "b", "j": "t"}[mode]
        with open("./_assets/objects/%s/%s" % (first_two_letters, hash), "r"+write_mode) as f:
            content = f.read()
        if mode == "j": content = json.loads(content)
        return content
    else: return fetch_asset(id, name, mode, store=True)

def get_asset_from_hash(asset_hash:str, mode:str="t") -> str|bytes|dict:
    '''Gets an asset from its hash. `mode` can be "t" (text), "b" (bytes), or "j" (json)'''
    first_two_letters = asset_hash[:2]
    write_mode = {"t": "t", "b": "b", "j": "t"}[mode]
    if os.path.exists("./_assets/objects/%s/%s" % (first_two_letters, asset_hash)):
        with open("./_assets/objects/%s/%s" % (first_two_letters, asset_hash), "r"+write_mode) as f:
            content = f.read()
        if mode == "j": content = json.loads(content)
    else:
        content = fetch_asset_from_hash(asset_hash, mode)
        if content == "j": write_content = json.dumps(content, indent=2)
        else: write_content = content
        if not os.path.exists("./_assets/objects/%s" % first_two_letters): os.mkdir("./_assets/objects/%s" % first_two_letters)
        with open("./_assets/objects/%s/%s" % (first_two_letters, asset_hash), "w"+write_mode) as f:
            f.write(write_content)
    return content

def get_assets_from_hash(hashes:list[str], mode:str="t", collect:bool=False) -> list[str|bytes|dict]:
    '''Gets multiple assets from their hashes. `mode` can be "t" (text), "b" (bytes), or "j" (json). Set `collect` to True to return the contents'''
    if collect: output = []
    for asset_hash in hashes:
        content = get_asset_from_hash(asset_hash, mode)
        if collect: output.append(content)
    if collect: return output

def get_assets(id:str, names:list[str], mode:str="t", collect:bool=False) -> list[str|bytes|dict]:
    '''Gets multiple assets from their ids and names. `mode` can be "t" (text), "b" (bytes), or "j" (json). Set `collect` to True to return the contents'''
    hashes = get_hashes(id, names)
    if collect: output = []
    for name in names:
        content = get_asset(id, name, mode, hashes[name])
        if collect: output.append(content)
    if collect: return output

def get_asset_version(version:str, name:str, mode:str="t") -> str|bytes|dict:
    if os.path.exists("./_versions/%s/assets/%s" % (version, name)):
        write_mode = {"t": "t", "b": "b", "j": "t"}[mode]
        with open("./_versions/%s/assets/%s" % (version, name), "r"+write_mode) as f:
            content = f.read()
        if mode == "j": content = json.loads(content)
        return content
    else:
        id = VersionJson.get_asset_index(version)
        return fetch_asset(id, name, mode, version, store=False, store_in_version=True)

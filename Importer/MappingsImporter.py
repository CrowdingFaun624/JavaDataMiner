'''Imports the client or server jar'''

import os

import Importer.VersionJson as VersionJson
import Importer.WebRequest as WebRequest

def fetch_client(version:str, store:bool=True) -> str:
    '''Fetches the client using the version name'''
    version_json = VersionJson.get_version_json(version)
    url = version_json["downloads"]["client_mappings"]["url"]
    mappings = WebRequest.web_request(url, "t")
    if store:
        with open("./_versions/%s/client.txt" % version, "wt") as f:
            f.write(mappings)
    return mappings

def fetch_server(version:str, store:bool=True) -> str:
    '''Fetches the server using the version name'''
    version_json = VersionJson.get_version_json(version)
    url = version_json["downloads"]["server_mappings"]["url"]
    mappings = WebRequest.web_request(url, "t")
    if store:
        with open("./_versions/%s/server.txt" % version, "wt") as f:
            f.write(mappings)
    return mappings

def get_client(version:str) -> str:
    '''Gets the client mappings from the file, or the url if the file does not exist'''
    if os.path.exists("./versions/%s/client.txt" % version):
        with open("./_versions/%s/client.txt" % version, "rt") as f:
            return f.read()
    else: return fetch_client(version, store=True)

def get_server(version:str) -> str:
    '''Gets the server mappings from the file, or the url if the file does not exist'''
    if os.path.exists("./_versions/%s/server.txt" % version):
        with open("./_versions/%s/server.txt" % version, "rt") as f:
            return f.read()
    else: return fetch_server(version, store=True)

def get(version:str, side:str) -> str:
    '''Gets the mappings from the given side (client or server), or the url if the file does not exist'''
    if side == "client": return get_client(version)
    elif side == "server": return get_server(version)
    else: raise KeyError("invalid side: %s" % side)

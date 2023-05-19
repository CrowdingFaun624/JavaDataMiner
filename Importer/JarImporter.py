'''Imports the client or server jar'''

import os
import shutil
import zipfile

import Importer.Manifest as Manifest
import Importer.VersionJson as VersionJson
import Importer.WebRequest as WebRequest

def fetch_client(version:str) -> None:
    '''Fetches the client using the version name'''
    version_json = VersionJson.get_version_json(version)
    url = version_json["downloads"]["client"]["url"]
    with open("./_versions/%s/client.jar" % version, "wb") as f:
        f.write(WebRequest.web_request(url, "b"))

def fetch_server(version:str) -> None:
    '''Fetches the server using the version name'''
    version_json = VersionJson.get_version_json(version)
    url = version_json["downloads"]["server"]["url"]
    with open("./_versions/%s/server.jar" % version, "wb") as f:
        f.write(WebRequest.web_request(url, "b"))

def fetch_unzipped_client(version:str) -> None:
    '''Unzips the version's client jar'''
    fetch_unzipped(version, "client")

def fetch_unzipped_server(version:str) -> None:
    '''Unzips the version's server jar'''
    fetch_unzipped(version, "server")

def fetch_unzipped(version:str, side:str) -> None:
    '''Unzips the version's specified jar'''
    if side not in ("client", "server"): raise ValueError("%s is not a valid side!" % side)
    if not os.path.exists("./_versions/%s/%s.zip" % (version, side)):
        if not os.path.exists("./_versions/%s/%s.jar" % (version, side)): fetch(version, side)
        shutil.copy("./_versions/%s/%s.jar" % (version, side), "./_versions/%s/%s.zip" % (version, side))
    with zipfile.ZipFile("./_versions/%s/%s.zip" % (version, side)) as zip_file:
        zip_file.extractall("./_versions/%s/%s_unzipped" % (version, side))
    if os.path.exists("./_versions/%s/%s.zip" % (version, side)):
        os.remove("./_versions/%s/%s.zip" % (version, side)) # clean up to save space

def get_unzipped_client(version:str) -> None:
    get_unzipped(version, "client")

def get_unzipped_server(version:str) -> None:
    get_unzipped(version, "server")

def get_unzipped(version:str, side:str) -> None:
    '''Fetches the unzipped file if it does not already exist'''
    if not os.path.exists("./_versions/%s/%s_unzipped" % (version, side)):
        fetch_unzipped(version, side)

def fetch(version:str, side:str) -> None:
    '''Fetches the file based on the side using the version name'''
    if side == "client": fetch_client(version)
    elif side == "server": fetch_server(version)
    else: raise ValueError("%s is not a valid side!" % side)

def main() -> None:
    '''Asks what version to fetch'''
    fetch_client(input("Import client from version: "))

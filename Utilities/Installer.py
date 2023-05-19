import json
import os
import shutil

import Importer.JarImporter as JarImporter
import Importer.VersionJson as VersionJson

def install(version:str, store:bool=False) -> None:
    '''Installs the version into .minecraft/versions. Set `store` to True to store the json (jar is always stored).'''
    if not os.path.exists((jar_path:=os.path.join("./_versions", version, "client.jar"))):
        JarImporter.fetch_client(version)
    if not os.path.exists((version_json_path:=os.path.join("./_versions", "version", "version.json"))):
        version_json = json.dumps(VersionJson.fetch_version_json(version))
        if store:
            with open(os.path.join("./_versions", version, "version.json"), "wt") as f:
                f.write(json.dumps(json.loads(version_json), indent=2))
    else:
        with open(version_json_path, "rt") as f:
            version_json = json.dumps(json.loads(f.read()))
    dest_path = os.path.join(os.getenv('APPDATA'), ".minecraft", "versions", version)
    if not os.path.exists(dest_path): os.mkdir(dest_path) # create version folder in versions
    jar_dest_path = os.path.join(dest_path, version+".jar")
    json_dest_path = os.path.join(dest_path, version+".json")
    if not os.path.exists(jar_dest_path): shutil.copy(jar_path, jar_dest_path)
    if not os.path.exists(json_dest_path):
        with open(json_dest_path, "wt") as f:
            f.write(version_json)
    jar_success = os.path.exists(jar_dest_path)
    json_success = os.path.exists(json_dest_path)
    if not jar_success: print("Unable to transfer %s jar!" % version)
    if not json_success: print("Unable to transfer %s json!" % version)

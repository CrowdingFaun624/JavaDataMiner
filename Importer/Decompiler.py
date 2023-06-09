'''Decompiles a .class or .jar file'''

import os
import subprocess
import zipfile

import Importer.JarImporter as JarImporter
import Importer.JarRemapper as JarRemapper
import Importer.Manifest as Manifest
import Importer.MappingsImporter as MappingsImporter

def decompile(version:str, side:str):
    cfr_path = "./Lib/cfr-0.146.jar"
    if MappingsImporter.has_mappings(version):
        jar_path = "./_versions/%s/%s_remapped.jar" % (version, side)
        if not os.path.exists(jar_path): JarRemapper.remap(version, side)
    else:
        jar_path = "./_versions/%s/%s.jar" % (version, side)
        if not os.path.exists(jar_path): JarImporter.fetch_client(version)
    if not os.path.exists(cfr_path): raise FileNotFoundError("CFR does not exist!")
    if os.path.isdir(jar_path) or os.path.isdir(cfr_path): raise FileNotFoundError("What should be a file is a directory!")
    output_path = "./_versions/%s/%s_decompiled" % (version, side)
    # f'./src/{version}/{side}'
    subprocess.run(['java',
                    '-Xmx4G',
                    '-Xms1G',
                    '-jar', cfr_path.__str__(),
                    jar_path.__str__(),
                    '--outputdir', output_path,
                    '--caseinsensitivefs', 'true',
                    "--silent", "true"
                    ], check=True, capture_output=False)
    os.remove(jar_path)
    os.remove(os.path.join(output_path, "summary.txt"))

def get_decompiled(version:str, side:str="client") -> None:
    '''Decompiles the given version's client or unzips an archive if available'''
    zip_path = os.path.join("./_versions", version, "%s_decompiled.zip" % side)
    dest_path = os.path.join("./_versions", version, "%s_decompiled" % side)
    if os.path.exists(dest_path): return
    elif os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path) as zip_file:
            zip_file.extractall(dest_path)
        os.remove(zip_path)
    else:
        decompile(version, side)

def get_decompiled_client(version:str) -> None:
    get_decompiled(version, "client")

def get_decompiled_server(version:str) -> None:
    get_decompiled(version, "server")

def decompile_client(version:str) -> None:
    '''Decompiles the given version's client'''
    decompile(version, "client")

def decompile_server(version:str) -> None:
    '''Decompiles the given version's server'''
    decompile(version, "server")

def main() -> None:
    def get_user_input(display:str, options:list[str]) -> str:
        user_input = None
        while True:
            user_input = input(display)
            if user_input in options: return user_input
            else: continue
    versions = [version["id"] for version in Manifest.get_manifest()["versions"]]
    selected_version = get_user_input("Select version: ", versions)
    selected_side = get_user_input("Select side (client/server): ", ["client", "server"])
    decompile(selected_version, selected_side)

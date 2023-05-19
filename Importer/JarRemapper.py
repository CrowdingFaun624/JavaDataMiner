'''Remaps a .jar file according to mappings'''

import os
import subprocess

import Importer.JarImporter as JarImporter
import Importer.MappingsEncoder as MappingsEncoder

def remap(version:str, side:str):
    '''Remaps the jar file from the given version and side'''
    jar_path = "./_versions/%s/%s.jar" % (version, side)
    mappings_path = "./_versions/%s/%s.tsrg" % (version, side)
    specialsource_path = "./Lib/SpecialSource-1.9.1.jar"
    if not os.path.exists(jar_path): JarImporter.fetch(version, side)
    if not os.path.exists(mappings_path): MappingsEncoder.create_mappings(version, side)
    if not os.path.exists(specialsource_path): raise FileNotFoundError("specialsource is missing!")
    if os.path.isdir(jar_path) or os.path.isdir(mappings_path) or os.path.isdir(specialsource_path): raise FileNotFoundError("What should be a file is a directory!")
    output_path = "./_versions/%s/%s_remapped.jar" % (version, side)
    subprocess.run(['java',
                    '-jar', specialsource_path.__str__(),
                    '--in-jar', jar_path.__str__(),
                    '--out-jar', output_path.__str__(),
                    '--srg-in', mappings_path.__str__(),
                    "--kill-lvt"  # kill snowmen
                    ], check=True, capture_output=True)

def remap_client(version:str) -> None:
    '''Remaps the given version's client.jar'''
    remap(version, "client")

def remap_server(version:str) -> None:
    '''Remaps the given version's server.jar'''
    remap(version, "server")

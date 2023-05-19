'''Decompiles a .class or .jar file'''

import os
import subprocess

import Importer.JarRemapper as JarRemapper

def decompile(version:str, side:str):
    jar_path = "./_versions/%s/%s_remapped.jar" % (version, side)
    cfr_path = "./Lib/cfr-0.146.jar"
    if not os.path.exists(jar_path): JarRemapper.remap(version, side)
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

def decompile_client(version:str) -> None:
    '''Decompiles the given version's client'''
    decompile(version, "client")

def decompile_server(version:str) -> None:
    '''Decompiles the given version's server'''
    decompile(version, "server")

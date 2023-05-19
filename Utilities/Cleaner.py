'''Clears files that may take up lots of space in the ./_versions folder'''

import json
import os
import shutil

def clear_compressed_mappings(versions:list[str]=None) -> None:
    '''Removes client_mappings_compressed.txt and server_mappings_compressed.txt'''
    if versions is None: versions = os.listdir("./_versions")
    for version in versions:
        if not os.path.isdir("./_versions/%s" % version): continue
        if os.path.exists("./_versions/%s/client_mappings_compressed.txt" % version):
            os.remove("./_versions/%s/client_mappings_compressed.txt" % version)
        if os.path.exists("./_versions/%s/server_mappings_compressed.txt" % version):
            os.remove("./_versions/%s/server_mappings_compressed.txt" % version)

def clear_empty_folders(versions:list[str]=None) -> None:
    '''Removes empty version folders from ./_versions'''
    if versions is None: versions = os.listdir("./_versions")
    for version in versions:
        if not os.path.isdir("./_versions/%s" % version): continue
        if len(os.listdir("./_versions/%s" % version)) == 0:
            os.rmdir("./_versions/%s" % version)

def clear_extremely_trivial_data(versions:list[str]=None) -> None:
    '''Removes very trivial files in ./_versions/<version>/data that can be recovered very quickly:
    * subtitles.json'''
    trivial_data_files = ["subtitles.json"]
    clear_trivial_data(versions, trivial_data_files)

def clear_mappings(versions:list[str]=None) -> None:
    '''Removes client.txt and server.txt'''
    if versions is None: versions = os.listdir("./_versions")
    for version in versions:
        if not os.path.isdir("./_versions/%s" % version): continue
        if os.path.exists("./_versions/%s/client.txt" % version):
            os.remove("./_versions/%s/client.txt" % version)
        if os.path.exists("./_versions/%s/server.txt" % version):
            os.remove("./_versions/%s/server.txt" % version)

def clear_mappings_tsrg(versions:list[str]=None) -> None:
    '''Removes client.tsrg and server.tsrg'''
    if versions is None: versions = os.listdir("./_versions")
    for version in versions:
        if not os.path.isdir("./_versions/%s" % version): continue
        if os.path.exists("./_versions/%s/client.tsrg" % version):
            os.remove("./_versions/%s/client.tsrg" % version)
        if os.path.exists("./_versions/%s/server.tsrg" % version):
            os.remove("./_versions/%s/server.tsrg" % version)

def clear_trivial_data(versions:list[str]=None, trivial_data_files:list[str]=None) -> None:
    '''Removes trivial files in ./_versions/<version>/data that can be recovered quickly:
    * language.json
    * sound_events.json'''
    if versions is None: versions = os.listdir("./_versions")
    if trivial_data_files is None: trivial_data_files = ["language.json", "sound_events.json"]
    for version in versions:
        if not os.path.isdir("./_versions/%s" % version): continue
        if not os.path.exists("./_versions/%s/data" % version): continue
        for trivial_data_file in trivial_data_files:
            if os.path.exists("./_versions/%s/data/%s" % (version, trivial_data_file)):
                os.remove("./_versions/%s/data/%s" % (version, trivial_data_file))
        if len(os.listdir("./_versions/%s/data" % version)) == 0:
            os.rmdir("./_versions/%s/data" % version)

def clear_unzipped(versions:list[str]=None) -> None:
    '''Removes client_unzipped and server_unzipped if they exist'''
    if versions is None: versions = os.listdir("./_versions")
    for version in versions:
        if not os.path.isdir("./_versions/%s" % version): continue
        if os.path.exists("./_versions/%s/client_unzipped" % version):
            shutil.rmtree("./_versions/%s/client_unzipped" % version)
        if os.path.exists("./_versions/%s/server_unzipped" % version):
            shutil.rmtree("./_versions/%s/server_unzipped" % version)

def sort_dict(input_dict:dict) -> dict:
    '''Sorts a dict by its keys, then values'''
    output = [(k, v) for k, v in input_dict.items()]
    output = sorted(output)
    output = dict(output)
    return output

def estimate_sizes(print_data:bool=True) -> dict[str,int]:
    def get_size(path:str) -> int:
        if os.path.isfile(path): return os.path.getsize(path)
        file_list = os.listdir(path)
        size = 0
        for file in file_list:
            if os.path.isdir(path+"/"+file):
                size += get_size(path+"/"+file)
            elif os.path.isfile(path+"/"+file):
                size += os.path.getsize(path+"/"+file)
        return size
    def fancify(data:dict[str,int]) -> str:
        output = {}
        for key, value in list(data.items()):
            output[key] = "{:,}".format(value) # adds commas
        output = json.dumps(output, indent=2)
        return output
    
    versions:dict[str,dict[str,int]] = {}
    version_list = os.listdir("./_versions")
    if "version_manifest.json" in version_list: version_list.remove("version_manifest.json")
    for version in version_list:
        files = {}
        file_list = os.listdir("./_versions/%s" % version)
        for file in file_list:
            files[file] = get_size("./_versions/%s/%s" % (version, file))
        versions[version] = files
    combined = {}
    for version, files in list(versions.items()):
        for file, size in list(files.items()):
            if file not in combined: combined[file] = size
            else: combined[file] += size
    combined = sort_dict(combined)
    if print_data: print(fancify(combined))
    return combined

def main() -> None:
    functions = {
        "clear_compressed_mappings": clear_compressed_mappings,
        "clear_empty_folders": clear_empty_folders,
        "clear_extremely_trivial_data": clear_extremely_trivial_data,
        "clear_mappings": clear_mappings,
        "clear_mappings_tsrg": clear_mappings_tsrg,
        "clear_trivial_data": clear_trivial_data,
        "clear_unzipped": clear_unzipped,
        "estimate_sizes": estimate_sizes
    }
    user_input = None
    while user_input not in functions:
        user_input = input("Select a function from [%s]: " % ", ".join(list(functions.keys())))
    functions[user_input]()

if __name__ == "__main__":
    main()
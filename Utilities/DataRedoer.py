'''For when you need to redo some data but don't want to delete all of the files individually'''

import os

import DataMiners.DataMiners as DataMiners
import Importer.Manifest as Manifest

def get_version_range(old_version_id:int, new_version_id:int):
    if old_version_id == new_version_id: return [new_version_id]
    else: return list(reversed(Manifest.get_version_list()))[old_version_id:new_version_id + 1]

def get_file_names() -> list[str]:
    return [dataminer.file_name for dataminer in list(DataMiners.all_dataminers.values())]

def main() -> None:
    def get_valid_input(text:str, options:list[str], print_options:bool=True) -> str:
        input_version = None
        while True:
            if input_version in options: return input_version
            if print_options:
                input_version = input(text % str(options))
            else: input_version = input(text)
    def get_version_input(text:str) -> str:
        return get_valid_input(text, Manifest.get_version_list(), False)
    old_version = get_version_input("Oldest version: ")
    new_version = get_version_input("Newest version: ")
    old_version_id = Manifest.get_version_id(old_version)
    new_version_id = Manifest.get_version_id(new_version)
    if old_version_id > new_version_id: raise IndexError(f"Old version specified (\"{old_version}\") occurs after the newer version (\"{new_version}\")!")
    version_range = get_version_range(old_version_id, new_version_id)
    user_input = get_valid_input(f"Are these versions correct (y/n)? %s\n" % str(version_range), ["y", "n"], print_options=False)
    if user_input != "y": return
    file_to_remove = get_valid_input("Which file should be removed? %s ", get_file_names(), True)
    for version in version_range:
        file_name = os.path.join("./_versions", version, "data", file_to_remove)
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed {file_name} from {version}")

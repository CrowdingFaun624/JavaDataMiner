import json
import os

import DataMiners.Language.Language as Language
import Importer.Manifest as Manifest

def get_all_language_keys() -> set[str]:
    file_path = "./Assets/all_language_keys.json"
    if os.path.exists(file_path):
        with open(file_path, "rt") as f:
            return set(json.loads(f.read()))
    else: return fetch_all_language_keys()

def fetch_all_language_keys() -> set[str]:
    sum_language = set()
    for version in Manifest.get_version_list():
        lang_file:dict[str,str] = Language.Language.get_data_file(version)
        if lang_file is None: continue
        keys = set(lang_file.keys())
        sum_language.update(keys)
    sum_language_list = list(sum_language)
    sum_language_list.sort()
    with open("./Assets/all_language_keys.json", "wt") as f:
        f.write(json.dumps(sum_language_list, indent=2))
    return sum_language

def main() -> None:
    fetch_all_language_keys()

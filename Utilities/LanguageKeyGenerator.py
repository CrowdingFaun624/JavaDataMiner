import json

import DataMiners.Language.Language as Language
import Importer.Manifest as Manifest

def main() -> None:
    sum_language = set()
    for version in Manifest.get_version_list():
        lang_file:dict[str,str] = Language.Language.get_data_file(version)
        if lang_file is None: continue
        keys = set(lang_file.keys())
        sum_language.update(keys)
    sum_language = list(sum_language)
    sum_language.sort()
    with open("./Assets/all_language_keys.json", "wt") as f:
        f.write(json.dumps(sum_language, indent=2))

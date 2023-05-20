import os

import Importer.Manifest as Manifest
import DataMiners.DataMiner as DataMiner
import DataMiners.DataMiners as DataMiners

import Comparison.DataComparer as DataComparer
import Comparison.DataMiners.BlocksComparer as BlocksComparer
import Comparison.DataMiners.SoundTypeBlocksComparer as SoundTypeBlocksComparer
import Comparison.DataMiners.SoundTypeComparer as SoundTypeComparer
import Comparison.ListComparer as ListComparer
import Comparison.DictionaryComparer as DictionaryComparer

all_comparers:dict[str,DataComparer.DataComparer] = {
    "blocks": BlocksComparer.BlocksComparer,
    "language": DictionaryComparer.DictionaryComparer,
    "sound_events": DictionaryComparer.DictionaryComparer,
    "sound_type": SoundTypeComparer.SoundTypeComparer,
    "sound_type_blocks": SoundTypeBlocksComparer.SoundTypeBlocksComparer,
    "subtitles": DictionaryComparer.DictionaryComparer
}

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
    old_version = get_version_input("Older version: ")
    new_version = get_version_input("Newer version: ")
    data_type = get_valid_input("Data type (%s): ", list(DataMiners.all_dataminers.keys()))
    old_data = DataMiner.get_dataminer(old_version, DataMiners.all_dataminers[data_type]).activate(old_version)
    new_data = DataMiner.get_dataminer(new_version, DataMiners.all_dataminers[data_type]).activate(new_version)
    data = all_comparers[data_type]().activate(old_data, new_data)
    file_name = DataComparer.get_valid_file_name(data_type)
    with open(os.path.join("./_comparisons", file_name), "wt") as f:
        f.write(data)

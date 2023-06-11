import os

import Importer.Manifest as Manifest
import DataMiners.DataMiner as DataMiner
import DataMiners.DataMiners as DataMiners

import Comparison.DataComparer as DataComparer
import Comparison.Blocks.Blocks as BlocksComparer
import Comparison.SoundEvents.SoundEvents as SoundEvents
import Comparison.SoundTypeBlocks.SoundTypeBlocks as SoundTypeBlocksComparer
import Comparison.SoundType.SoundType as SoundTypeComparer
import Comparison.ListComparer as ListComparer
import Comparison.DictionaryComparer as DictionaryComparer

all_comparers:dict[str,DataComparer.DataComparer] = {
    "blocks": BlocksComparer.BlocksComparer,
    "language": DictionaryComparer.DictionaryComparer,
    "sound_events": SoundEvents.SoundEvents,
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
    dataminers = DataMiners.all_dataminers[data_type]
    old_data = DataMiner.get_data_file(old_version, dataminers.file_name, dataminers.dataminers)
    new_data = DataMiner.get_data_file(new_version, dataminers.file_name, dataminers.dataminers)
    comparer:DataComparer.DataComparer = all_comparers[data_type]()
    data = comparer.activate(old_data, new_data, old_version, new_version)
    if data is None: return
    file_name = DataComparer.get_valid_file_name(data_type)
    with open(os.path.join("./_comparisons", file_name), "wt") as f:
        f.write(data)

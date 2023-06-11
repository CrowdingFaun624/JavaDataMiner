import os

import Comparison.Comparers as Comparers
import Comparison.DataComparer as DataComparer
import DataMiners.DataMiner as DataMiner
import DataMiners.DataMiners as DataMiners
import Importer.Manifest as Manifest

def main() -> None:
    def get_valid_input(text:str, options:list[str], print_options:bool=True) -> str:
        input_version = None
        while True:
            if input_version in options: return input_version
            if print_options:
                input_version = input(text % str(options))
            else: input_version = input(text)
    data_type = get_valid_input("Data type (%s): ", list(DataMiners.all_dataminers.keys()))
    dataminers = DataMiners.all_dataminers[data_type]
    version_list = Manifest.get_version_list(reverse=True) # oldest to newest
    comparer:DataComparer.DataComparer = Comparers.all_comparers[data_type]()
    destination_folder = os.path.join("./_comparisons", data_type)
    if os.path.exists(destination_folder):
        for file in os.listdir(destination_folder):
            os.remove(os.path.join(destination_folder, file))
    else: os.mkdir(destination_folder)
    for old_version in version_list:
        old_version_id = Manifest.get_version_id(old_version)
        new_version_id = old_version_id + 1
        if new_version_id >= len(version_list): continue
        new_version = version_list[new_version_id]
        old_data = DataMiner.get_data_file(old_version, dataminers.file_name, dataminers.dataminers)
        new_data = DataMiner.get_data_file(new_version, dataminers.file_name, dataminers.dataminers)
        if old_data is None or new_data is None: continue
        data = comparer.activate(old_data, new_data, old_version, new_version)
        if data is None: continue
        file_name = DataComparer.get_valid_file_name(data_type, data_type)
        with open(os.path.join("./_comparisons", data_type, file_name), "wt") as f:
            f.write(data)

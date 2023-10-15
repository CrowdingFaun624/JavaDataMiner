import os
from typing import Any

import Comparison.Comparer as Comparer
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer

class DataComparer():
    def __init__(self, add_message="Added %s\n", change_message="Changed %s to %s\n", remove_message="Removed %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message

    def analyze(self, comparison:Any, version1:str, version2:str, total:int) -> str|None:
        pass

    def activate(self, data1:Any, data2:Any, version1:str, version2:str) -> str|None:
        '''Compares data'''
        pass

    def compare(self, data1:Any, data2:Any, type_hint:type|None=None) -> Any:
        return Comparer.compare(data1, data2, type_hint)
    
    def get_normalizer(self, version:str) -> Normalizer.Normalizer:
        normalizer_list = self.get_normalizers()
        for normalizer in normalizer_list:
            if normalizer.is_valid_version(version): return normalizer
        else: raise KeyError("No data normalizer found for %s!" % version)
    
    def get_normalizers(self) -> list[Normalizer.Normalizer]: ...

    def sort_dict(self, input_dict:dict, by_values:bool=False) -> dict:
        '''Sorts a dict by its keys, then values'''
        if by_values: output = [(v, k) for k, v in input_dict.items()]
        else: output = [(k, v) for k, v in input_dict.items()]
        output = sorted(output)
        if by_values: output = [(v, k) for k, v in output]
        output = dict(output)
        return output

def get_valid_file_name(base_name:str, sub_path:str="") -> str:
    file_path = os.path.join("./_comparisons", sub_path) if sub_path != "" else "./_comparisons" #os.path.join is very dumb and stupid
    files = set(os.listdir(file_path))
    for index in range(10000):
        index_str = str(index)
        index_str = "0"*(4-len(index_str)) + index_str
        file_name = base_name + index_str + ".txt"
        if file_name not in files: return file_name
    else: raise FileExistsError("Could not find valid path name for \"%s%s\"!" % (sub_path, base_name))

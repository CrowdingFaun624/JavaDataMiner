import os

import Comparison.Comparer as Comparer
import Comparison.Difference as D

class DataComparer():
    def __init__(self, add_message="Added %s\n", change_message="Changed %s to %s\n", remove_message="Removed %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
    def activate(self, data1:any, data2:any) -> str:
        '''Compares data'''
        pass
    def compare(self, data1:any, data2:any) -> any:
        return Comparer.compare(data1, data2)

def get_valid_file_name(base_name:str, sub_path:str="") -> str:
    file_path = os.path.join("./_comparisons", sub_path) if sub_path != "" else "./_comparisons" #os.path.join is very dumb and stupid
    files = set(os.listdir(file_path))
    for index in range(10000):
        index_str = str(index)
        index_str = "0"*(4-len(index_str)) + index_str
        file_name = base_name + index_str + ".txt"
        if file_name not in files: return file_name
    else: raise FileExistsError("Could not find valid path name for \"%s%s\"!" % (sub_path, base_name))

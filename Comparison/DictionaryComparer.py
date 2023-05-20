import json

import Comparison.DataComparer as DataComparer
import Comparison.Difference as D

class DictionaryComparer(DataComparer.DataComparer):
    '''Compares two shallow dictionaries'''
    def __init__(self, add_message="Added %s: %s\n", change_message="Changed %s from %s to %s\n", remove_message="Removed %s: %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
    def activate(self, data1:dict, data2:dict) -> str:
        comparison:dict = self.compare(data1, data2)
        additions:list[tuple[str|int|float|bool,D.Difference]] = []
        changes:list[tuple[str|int|float|bool,D.Difference]] = []
        removals:list[tuple[str|int|float|bool,D.Difference]] = []
        for key, value in list(comparison.items()):
            if not isinstance(key, (str, int, float, bool)): raise TypeError("Key is not a valid type!")
            if not isinstance(value, (str, int, float, bool, D.Difference)): raise TypeError("Dictionary is not shallow!")
            if not isinstance(value, D.Difference): continue
            if value.is_addition(): additions.append((key, value))
            elif value.is_change(): changes.append((key, value))
            elif value.is_removal(): removals.append((key, value))
            output = ""
            for key, value in additions: output += self.add_message % (json.dumps(key), json.dumps(value.new))
            for key, value in changes: output += self.change_message % (json.dumps(key), json.dumps(value.old), json.dumps(value.new))
            for key, value in removals: output += self.remove_message % (json.dumps(key), json.dumps(value.old))
        return output

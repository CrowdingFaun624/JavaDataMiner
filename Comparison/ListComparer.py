import json

import Comparison.DataComparer as DataComparer
import Comparison.Difference as D

class ListComparer(DataComparer.DataComparer):
    '''Compares two lists'''
    def __init__(self, add_message="Added item %s: %s\n", change_message="Changed item %s from %s to %s\n", remove_message="Removed item %s: %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
    def activate(self, data1:list, data2:list) -> str:
        comparison:list = self.compare(data1, data2)
        additions:list[tuple[int,D.Difference]] = []
        changes:list[tuple[int,D.Difference]] = []
        removals:list[tuple[int,D.Difference]] = []
        for index, value in enumerate(comparison):
            if not isinstance(value, D.Difference): continue
            if value.type == D.ADD: additions.append((index, value))
            elif value.type == D.CHANGE: changes.append((index, value))
            elif value.type == D.REMOVE: removals.append((index, value))
        output = ""
        for index, value in additions: output += self.add_message % (index, json.dumps(value.new, indent=2))
        for index, value in changes: output += self.change_message % (index, json.dumps(value.old, indent=2), json.dumps(value.new, indent=2))
        for index, value in removals: output += self.remove_message % (index, json.dumps(value.old, indent=2))
        return output

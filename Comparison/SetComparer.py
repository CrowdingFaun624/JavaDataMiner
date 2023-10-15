import json
from typing import Any

import Comparison.DataComparer as DataComparer
import Comparison.Difference as D

class SetComparer(DataComparer.DataComparer):
    '''Compares two lists'''
    def __init__(self, add_message="\tAdded %s\n", change_message="\tChanged %s to %s\n", remove_message="\tRemoved %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message

    def analyze(self, comparison:set, version1:str, version2:str, total:int) -> str|None:
        additions:list[D.Difference] = []
        changes:list[D.Difference] = []
        removals:list[D.Difference] = []
        for value in comparison:
            if not isinstance(value, D.Difference): continue
            if value.is_addition(): additions.append(value)
            elif value.is_change(): changes.append(value)
            elif value.is_removal(): removals.append(value)
        additions.sort()
        changes.sort()
        removals.sort()
        if len(additions) == 0 and len(removals) == 0 and len(changes) == 0: return None
        output = f"{version2} (from {version1})\n\nTotal: {total} (+{len(additions)}, -{len(removals)})\n\n"
        if len(additions) > 0:
            output += "Additions:\n"
            for value in additions:
                output += self.add_message % json.dumps(value.new)
            output += "\n"
        if len(removals) > 0:
            output += "Removals:\n"
            for value in removals:
                output += self.remove_message % json.dumps(value.old)
            output += "\n"
        if len(changes) > 0:
            output += "Changes:\n"
            for value in changes:
                output += self.change_message % (json.dumps(value.old), json.dumps(value.new))
            output += "\n"
        return output

    def activate(self, data1:set, data2:set, version1:str, version2:str) -> str:
        comparison:list = self.compare(set(data1), set(data2))
        return self.analyze(comparison, version1, version2, len(data2))

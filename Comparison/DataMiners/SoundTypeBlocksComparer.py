import json

import Comparison.DataComparer as DataComparer
import Comparison.Difference as D

class SoundTypeBlocksComparer(DataComparer.DataComparer):
    def __init__(self, add_message="Added type %s with blocks:\n%s\n", change_message="CHANGE ERROR\n", remove_message="Removed type %s\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
    def reformat(data:dict[str,list[str]]) -> dict[str,set[str]]:
        output:dict[str,set[str]] = {}
        for type_name, type_content in list(data.items()):
            if isinstance(type_content, D.Difference):
                old = set(type_content.old) if type_content.old is not None else None
                new = set(type_content.new) if type_content.new is not None else None
                output[type_name] = D.Difference(type_content.type, old, new)
            else:
                output[type_name] = set(type_content)
    def get_blocks_string(self, blocks_list:set[str]) -> str:
        output = ""
        for block in blocks_list:
            output += "\t" + str(block) + "\n"
    def activate(self, data1:dict[str,list[str]], data2:dict[str,list[str]]) -> str:
        comparison:dict[str,set[str]] = self.compare(self.reformat(data1), self.reformat(data2))
        output = ""
        type_additions:dict[str,list[str]] = {}
        type_removals:dict[str,list[str]] = {}
        for type_name, type_content in list(comparison.items()):
            if isinstance(type_content, D.Difference):
                if type_content.type == D.CHANGE:
                    raise ValueError("Type should not be change!")
                elif type_content.type == D.ADD:
                    output += self.add_message % type_name, self.get_blocks_string(type_content.new)
                elif type_content.type == D.REMOVE:
                    output += self.remove_message % type_name
            else:
                for block in type_content:
                    if not isinstance(block, D.Difference): continue
                    if block.type == D.CHANGE:
                        raise ValueError("Sets should not have changes!")
                    elif block.type == D.ADD:
                        if type_name not in type_additions: type_additions[type_name] = []
                        type_additions[type_name].append(block.new)
                    elif block.type == D.REMOVE:
                        if type_name not in type_removals: type_removals[type_name] = []
                        type_removals[type_name].append(block.old)
        if len(type_additions) > 0:
            output += "\n"
            for type_name, additions in list(type_additions.items()):
                output += "Added these blocks to %s:\n"
                output += self.get_blocks_string(additions)
        if len(type_removals) > 0:
            output += "\n"
            for type_name, removals in list(type_removals.items()):
                output += "Removed these blocks from %s:\n"
                output += self.get_blocks_string(removals)
        return output

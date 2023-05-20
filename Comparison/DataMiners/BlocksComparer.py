import Comparison.Comparer as Comparer
import Comparison.DataComparer as DataComparer
import Comparison.Difference as D

class BlocksComparer(DataComparer.DataComparer):
    def __init__(self, add_message="Add block %s with:\n\t%s\n", change_message="Changed block's %s to %s.\n", remove_message="Removed block %s.\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
    def stringify(input_object:any) -> str:
        functions = {str: lambda x: x, list: BlocksComparer.stringify_list}
        return functions[type(input_object)](input_object)
    def stringify_list(input_list:list[str]) -> str:
        input_strings = [BlocksComparer.stringify(item) for item in input_list]
        if len(input_strings) == 0: return "[empty list]"
        elif len(input_strings) == 1: return input_strings[0]
        elif len(input_strings) == 2: return "%s and %s" % (input_strings[0], input_strings[1])
        else:
            return ", ".join(input_strings[:-1]) + ", and " + input_strings[-1]
    def get_properties_string(self, properties:dict[str,any]) -> str:
        '''Gets a string separated by newlines from a block_properties dict'''
        MESSAGE = "%s: %s"
        output = []
        for property, property_content in list(properties.items()):
            output.append(MESSAGE % (property, BlocksComparer.stringify(property_content)))
        return "\n\t".join(output)
    def activate(self, data1:dict[str,dict[str,any]], data2:dict[str,dict[str,any]]) -> str:
        comparison:dict[str,dict[str,any]] = Comparer.compare(data1, data2)
        output = ""
        for block_name, block_properties in list(comparison.items()):
            if isinstance(block_properties, D.Difference):
                if block_properties.is_change():
                    raise ValueError("Type should not be change!")
                elif block_properties.is_addition():
                    output += self.add_message % (block_name, self.get_properties_string(block_properties.new))
                elif block_properties.is_removal():
                    output += self.remove_message % block_name
            else:
                has_changes = False
                for property, property_contents in list(block_properties.items()):
                    if isinstance(property_contents, D.Difference):
                        if property_contents.is_addition():
                            if not has_changes: has_changes = True; output += "%s:\n" % block_name
                            output += "\tAdded property %s: %s\n" % (property, BlocksComparer.stringify(property_contents.new))
                        elif property_contents.is_change():
                            if not has_changes: has_changes = True; output += "%s:\n" % block_name
                            output += "\tChanged property %s from %s to %s\n" % (property, BlocksComparer.stringify(property_contents.old), BlocksComparer.stringify(property_contents.new))
                        elif property_contents.is_removal():
                            if not has_changes: has_changes = True; output += "%s:\n" % block_name
                            output += "\tRemoved property %s\n" % property
        return output

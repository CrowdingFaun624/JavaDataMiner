import Comparison.Comparer as Comparer
import Comparison.DataComparer as DataComparer
import Comparison.Difference as D

class SoundTypeComparer(DataComparer.DataComparer):
    def __init__(self, add_message="Added sound type %s:\n", change_message="Changed sound type %s:\n", remove_message="Removed sound type %s:\n"):
        self.add_message = add_message
        self.change_message = change_message
        self.remove_message = remove_message
    def get_properties_string(self, properties:dict[str,int|str|D.Difference], only_differences:bool=False) -> str:
        SINGLE = "\t%s: %s\n"
        DOUBLE = "\t%s: %s -> %s\n"
        output = ""
        for property_name, property_value in list(properties.items()):
            if isinstance(property_value, D.Difference) or not only_differences:
                if isinstance(property_value, D.Difference):
                    if property_value.is_change():
                        output += DOUBLE % (property_name, property_value.old, property_value.new)
                    elif property_value.is_addition():
                        output += SINGLE % (property_name, property_value.new)
                    elif property_value.is_removal():
                        output += SINGLE % (property_name, property_value.old)
                else:
                    output += SINGLE % (property_name, property_value)
        return output
    def activate(self, data1:dict[str,dict[str,int|str]], data2:dict[str,dict[str,int|str]]) -> str:
        comparison:dict[str,dict[str,int|str]] = Comparer.compare(data1, data2)
        output = ""
        for sound_type_name, sound_type_properties in list(comparison.items()):
            if isinstance(sound_type_properties, D.Difference):
                if sound_type_properties.is_addition():
                    output += self.add_message % sound_type_name
                    output += self.get_properties_string(sound_type_properties.new)
                if sound_type_properties.is_removal():
                    output += self.remove_message % sound_type_name
                    output += self.get_properties_string(sound_type_properties.old)
            else:
                has_changes = False
                for property_value in list(sound_type_properties.values()):
                    if isinstance(property_value, D.Difference): has_changes = True; break
                if has_changes:
                    output += self.change_message % sound_type_name
                    output += self.get_properties_string(sound_type_properties, True)
        return output

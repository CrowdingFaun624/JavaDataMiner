from typing import Any

try:
    import Comparison.Difference as D
except ModuleNotFoundError:
    import Difference as D

def compare_simple(old:Any, new:Any) -> D.Difference:
    return D.Difference("c", old, new)

def compare_dict(old:dict, new:dict) -> dict:
    additions = {}
    changes = {}
    removals = {}
    for new_key, new_value in list(new.items()):
        if new_key not in old.keys():
            additions[new_key] = D.Difference("a", None, new_value)
    for old_key, old_value in list(old.items()):
        if old_key not in new.keys():
            removals[old_key] = D.Difference("r", old_value, None)
    for key in list(new.keys()):
        if key not in old: continue
        if new[key] != old[key]:
            changes[key] = compare(old[key], new[key])
    final = new.copy()
    final.update(additions)
    final.update(changes)
    final.update(removals)
    return final

def compare_list(old:list|tuple, new:list|tuple) -> list|tuple:
    def to_dict(data:list|tuple) -> dict:
        output = {}
        for index, value in enumerate(data):
            output[index] = value
        return output
    def de_dict(data_dict:dict, data_type:type) -> list|tuple:
        return data_type(list(data_dict.values()))
    data_type = type(old)
    old_dict = to_dict(old)
    new_dict = to_dict(new)
    final = compare_dict(old_dict, new_dict)
    return de_dict(final, data_type)

def compare_set(old:set|list, new:set|list) -> set:
    if isinstance(old, set) and isinstance(new, set):
        additions = set()
        removals = set()
        for new_item in new:
            if new_item not in old:
                additions.add(D.Difference("a", None, new_item))
        for old_item in old:
            if old_item not in new:
                removals.add(D.Difference("r", old_item, None))
        final = new.copy()
        final.update(additions)
        final.update(removals)
    elif isinstance(old, list) and isinstance(new, list):
        additions, removals = [], []
        for new_item in new:
            if new_item not in old:
                additions.append(D.Difference("a", None, new_item))
        for old_item in old:
            if old_item not in new:
                removals.append(D.Difference("r", old_item, None))
        final = new.copy()
        for addition in additions: final.append(addition)
        for removal in removals: final.append(removal)
    else: raise TypeError("Attempted to compare type %s as if it were a set!" % type(old))
    return final

def compare(old:Any, new:Any, type_hint:type|None=None) -> Any:
    '''Returns data of the same structure with different values replaced with difference objects at maximum depth'''
    if type(old) != type(new):
        raise TypeError("Old (%s) and new (%s) values are not the same type!" % (str(old), str(new)))
    if type_hint is None and (new_type:=type(new)) not in FUNCTIONS:
        raise TypeError("Type %s does not support comparison!" % new_type)
    if type_hint is None: return FUNCTIONS[type(new)](old, new)
    else: return FUNCTIONS[type_hint](old, new)

def stringify_data(data:Any) -> Any:
    '''Converts all Difference objects to strings in the data'''
    if isinstance(data, (str, int, float, bool, D.Difference)):
        return str(data)
    elif isinstance(data, dict):
        output = {}
        for key, value in list(data.items()):
            output[key] = stringify_data(value)
        return output
    else:
        output = []
        for value in data:
            output.append(stringify_data(value))
        output = type(data)(output)
        return output

FUNCTIONS = {
    str: compare_simple,
    int: compare_simple,
    float: compare_simple,
    bool: compare_simple,
    dict: compare_dict,
    tuple: compare_list,
    list: compare_list,
    set: compare_set
}

def test() -> None:
    val1 = {"key1": "val1", "key2": {"key3": "val3", "key4": "val4"}}
    val2 = {"key1": "val1", "key2": {"key4": "val4 changed", "key5": "val5"}}
    print(stringify_data(compare(val1, val2)))

if __name__ == "__main__":
    test()
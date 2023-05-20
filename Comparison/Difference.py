ADD = "a"
REMOVE = "r"
CHANGE = "c"

class Difference():
    def __init__(self, type:str, old_value, new_value) -> None:
        if type not in ("a", "r", "c"): raise ValueError("Invalid type!")
        type_dict = {"a": ADD, "r": REMOVE, "c": CHANGE}
        self.type = type_dict[type]
        self.old = old_value
        self.new = new_value
    def __str__(self) -> str:
        return self.type + ": " + str(self.old) + " -> " + str(self.new)
    def is_addition(self) -> bool:
        return self.type is ADD
    def is_change(self) -> bool:
        return self.type is CHANGE
    def is_removal(self) -> bool:
        return self.type is REMOVE

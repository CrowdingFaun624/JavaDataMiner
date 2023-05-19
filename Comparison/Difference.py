ADD = "a"
REMOVE = "r"
CHANGE = "c"

class Difference():
    def __init__(self, type:str, old_value, new_value) -> None:
        if type not in ("a", "r", "c"): raise ValueError("Invalid type!")
        self.type = type
        self.old = old_value
        self.new = new_value
    def __str__(self) -> str:
        return self.type + ": " + str(self.old) + " -> " + str(self.new)

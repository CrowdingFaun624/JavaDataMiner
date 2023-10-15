from typing import Callable
from functools import total_ordering

ADD = "a"
REMOVE = "r"
CHANGE = "c"

@total_ordering
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
    
    def cast(self, new_type:type|Callable) -> None:
        if self.old is not None: self.old = new_type(self.old)
        if self.new is not None: self.new = new_type(self.new)
    
    def __hash__(self):
        return hash((self.type, self.old, self.new))

    def _is_valid_operand(self, other) -> bool:
        return hasattr(other, "old") and hasattr(other, "new")
    
    def __eq__(self, other:"Difference") -> bool:
        if not self._is_valid_operand(other): return NotImplemented
        return (self.new, self.old) == (other.new, other.old)

    def __lt__(self, other:"Difference") -> bool:
        if not self._is_valid_operand(other): return NotImplemented
        if self.new is not None and other.new is not None: return self.new < other.new
        elif self.old is not None and other.old is not None: return self.old < other.old
        elif self.old is not None and other.new is not None: return self.old < other.new
        elif self.new is not None and other.old is not None: return self.new < other.old

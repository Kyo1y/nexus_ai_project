
from typing import List, Optional

class ColumnItem:
    field: str  # Column name
    func: Optional[str] = None
    as_name: Optional[str] = None

    def __init__(self, field: str, func: Optional[str] = None, as_name: Optional[str] = None) -> None:
        self.field = field
        self.func = func
        self.as_name = as_name

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ColumnItem) and self.field == __value.field and self.func == __value.func and self.as_name == __value.as_name

    def __str__(self):
        return f'{self.__class__.__name__}(field={self.field}, func={self.func}, as_name={self.as_name})'
    
    def __repr__(self) -> str:
        return self.__str__()


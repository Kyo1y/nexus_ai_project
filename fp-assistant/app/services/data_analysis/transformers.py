import json
import logging
import re

import pandas as pd

from datetime import datetime, date
from dataclasses import dataclass
from typing import Any, List, Dict, Union, Literal, Tuple


with open('app/data_manager/agents/parent_office2child.json', 'r') as f:
    parent_office2child = json.load(f)

class Range:
    field: str
    upper: Union[date, int, float, None] = None
    lower: Union[date, int, float, None] = None
    flip: bool = False
    dtype: type = None

    def __init__(self, field: str, lower: Union[date, int, float, None] = None, upper: Union[date, int, float, None] = None, flip: bool = False):
        if not (upper or lower):
            raise TypeError('__init__() must have either "upper" or "lower" provided')
        elif flip and not (upper and lower):
            raise TypeError('Should only use flip when "upper and "lower" are both passed. Flip reverses the logic so just change argument.')


        if isinstance(upper, str):
            self.upper = datetime.strptime(upper, '%Y-%m-%d').date()
        else:
            self.upper = upper
       
        if isinstance(lower, str):
            self.lower = datetime.strptime(lower, '%Y-%m-%d').date()
        else:
            self.lower = lower

        self.flip = flip
        self.field = field

        if self.upper:
            self.dtype = type(self.upper)
        elif self.lower:
            self.dtype = type(self.lower)

    def __call__(self, data: pd.DataFrame) -> pd.DataFrame:
        
        # if self.field not in data.columns:
        #     raise ValueError(f'Field {self.field} not in data')

        if self.dtype is date:
            # Ensure that column is date format
            filter_col = pd.to_datetime(data[self.field]).dt.date
        else:
            filter_col = data[self.field]

        if self.upper and self.lower:
            mask = (filter_col > self.lower) & (filter_col < self.upper)
        elif self.upper:
            mask = (filter_col < self.upper)
        elif self.lower:
            mask = (filter_col > self.lower)
        else:
            raise ValueError(f'Could not create mask, check period object, {self}')

        if self.flip:
            mask = ~mask

        return data.loc[mask]
    
    def negate(self):
        if self.upper and self.lower:
            self.flip = not self.flip
        elif self.upper:
            self.lower = self.upper
            self.upper = None
        elif self.lower:
            self.upper = self.lower
            self.lower = None
    
    def __str__(self):
        args = f'field={self.field}, lower={self.lower}, upper={self.upper}, flip={self.flip}, dtype={self.dtype}'
        return f'{self.__class__.__name__}({args})'

    def __repr__(self) -> str:
        return self.__str__()

class Value:
    field: str
    items: List[Any]
    negate: bool = False
    dtype: type = None

    def __init__(self, field: str, items: List[str], negate: bool = False):
        # Hacky way to do change for primary office code

        if field.strip() == 'prim_ofcd':
            office_codes = []
            for code in items:
                if not isinstance(code, str):
                    code = str(code)
                office_codes.extend(parent_office2child.get(code, []))
            items = office_codes
            if not items:
                items = parent_office2child['520']

        self.items = items
        self.field = field
        self.negate = negate
        if items:
            self.dtype = type(self.items[0])
        else:
            self.dtype = None


    def __call__(self, data: pd.DataFrame) -> pd.DataFrame:
        filter_col = data[self.field]
        mask = filter_col.isin(self.items)


        if self.negate:
            mask = ~mask

        return data.loc[mask]
    
    
    def __str__(self):
        args = f'field={self.field}, items={self.items}, negate={self.negate} dtype={self.dtype}'
        return f'{self.__class__.__name__}({args})'

    def __repr__(self) -> str:
        return self.__str__()


class FieldFilter:
    field: str
    operator: str
    value: Union[date, int, float, str, list]
    dtype: type = None

    def __init__(self, field: str, operator: str, value: Union[date, int, float, str, list]):
        self.field = field
        self.operator = operator
        self.value = value
        self.dtype = type(value)

    def __call__(self, data: pd.DataFrame) -> pd.DataFrame:
        if self.dtype is date:
            # Ensure that column is date format
            filter_col = pd.to_datetime(data[self.field]).dt.date
        else:
            filter_col = data[self.field]

        if self.operator == '>':
            mask = filter_col > self.value
        elif self.operator == '>=':
            mask = filter_col >= self.value
        elif self.operator == '<':
            mask = filter_col < self.value
        elif self.operator == '<=':
            mask = filter_col <= self.value
        elif self.operator == '==':
            mask = filter_col == self.value
        elif self.operator == 'in':
            mask = filter_col.isin(self.value)
        else:
            raise ValueError(f'Invalid operator: {self.operator}')

        return data.loc[mask]

    def __str__(self):
        args = f'FieldFilter(field={self.field}, operator={self.operator}, value={self.value}, dtype={self.dtype})'
        return args

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Grouping:
    by: Literal['agent']
    agg_dict: Dict[str, Tuple[str, str]]

    @property
    def columns(self):
        if self.by in ['agent', 'agent, name', 'name, agent']:
            return ['AgentCode', 'name']
    
    def __call__(self, data: pd.DataFrame) -> pd.DataFrame:
        grouped_df = data.groupby(self.columns, as_index=False)
        
        # Has to be "key": tuple("col", "func")
        agg_dict = {}
        for key, tuple_list in self.agg_dict.items():
            agg_dict[key] = tuple(tuple_list)
        print(agg_dict)
        results = grouped_df.agg(**agg_dict)

        return results


def create_filters(filter_json: List[Dict[str, Any]]) -> List[Range]:
    filters = []
    for filter_dict in filter_json:
        if 'items' in filter_dict:
            filter_obj = Value(**filter_dict)
        else:
            filter_obj = Range(**filter_dict)
        filters.append(filter_obj)
    return filters

def create_field_filters(filter_json: List[Dict[str, Any]]) -> List[FieldFilter]:
    filters = []
    for filter_dict in filter_json:
        # Only have one type currently, but can expand to decide what filter type to use
        filter_obj = Range(**filter_dict)
        filters.append(filter_obj)
    return filters
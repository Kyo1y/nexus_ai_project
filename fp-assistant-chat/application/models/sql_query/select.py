import re

from typing import List, Optional

from application.models.sql_query.column_item import ColumnItem

class SelectClause:
    text: str
    select_items: List[ColumnItem]
    def __init__(self, select_text: str):
        self.text = select_text
        self.select_items = SelectClause.process(select_text)
    
    def convert_items_to_agg_dict(self):
        # TODO: move logic to specific place for building payload
        func_coverter = {'avg': 'mean'}
        field_converter = {'*': 'pid'}  # Set to pid for wildcard

        agg_dict = {}
        for item in self.select_items:
            func_name = item.func
            if func_name:
                func_name = func_name.lower()
                # Update function name if needed
                func_name = func_coverter.get(func_name, func_name)

                field = item.field.lower()
                field = field_converter.get(field, field)
                agg_name = f'{func_name}_{field}'
                agg_dict[agg_name] = (field, func_name)
        return agg_dict
    
    @staticmethod
    def process(input_text: str) ->  List[ColumnItem]:
        chunks = chunk_select(input_text)
        extracted = [extract_chunk(chunk) for chunk in chunks]
        return extracted
    
    def get_field_funcs(self):
        field_func_list = []
        for item in self.select_items:
            field_func_list.append((item.field, item.func))
        return field_func_list

def chunk_select(input_text: str) -> List[str]:
    return [chunk.strip() for chunk in input_text.split(',')]

def extract_chunk(select_chunk: str) -> ColumnItem:
    if '(' in select_chunk:
        # Function on select
        match = re.search(r'([^(]+)\((.*)\)(\s+[Aa][Ss]\s+(.*))?', select_chunk)
        if match is not None:
            field = match.group(2)
            func = match.group(1)
            name = match.group(4)
            select_obj = ColumnItem(field, func, name)
            return select_obj
        else:
            raise ValueError(f'Failed to parse {select_chunk}')
        
    else:
        match = re.search(r'(\S*)(\s+[Aa][Ss]\s+(.*))?', select_chunk)
        if match:
            field = match.group(1)
            name = match.group(3)
            select_obj = ColumnItem(field, as_name=name)
            return select_obj
        else:
            raise ValueError(f'Failed to parse {select_chunk}')

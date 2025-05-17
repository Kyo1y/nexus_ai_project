
from __future__ import annotations

import re

from typing import List, Literal, Union

from application.models.sql_query import sql_query
from application.models.sql_query.column_item import ColumnItem

def is_numeric(maybe_num: str):
    """ Returns True if string is a number. """
    return maybe_num.replace('.','',1).isdigit()

class LogicStatement:
    text: str
    left_expression: str
    operator: str
    right_expression: str

    def __init__(self, text, left_expression, operator, right_expression) -> None:
        self.text = text
        # TODO: Make edits here to add flexibility to parsing more complex inputs
        #       Such as col1 - col2 > col3 + col4
        #       Current assuming left will have column and right will have value
        self.left_expression = parse_expression(left_expression)
        self.operator = operator

        # Check to convert
        if is_numeric(right_expression):
            if right_expression.isdigit():
                right_expression = int(right_expression)
            else:
                right_expression = float(right_expression)
        self.right_expression = right_expression
    
    def __str__(self):
        return f'{self.__class__.__name__}(left_expression={self.left_expression}, operator={self.operator}, right_expression={self.right_expression})'
    
    def __repr__(self) -> str:
        return self.__str__()

def parse_expression(expression: str):
    if '(' in expression:
        # Function on select
        match = re.search(r'([^(]+)\((.*)\)(\s+[Aa][Ss]\s+(.*))?', expression)
        if match is not None:
            field = match.group(2)
            func = match.group(1)
            name = match.group(4)
            # NOTE: If it is possible to have access to field list, can check if field is valid before making
            select_obj = ColumnItem(field, func, name)
            return select_obj
    return expression

class LogicCombiner:
    kind: Literal['AND', 'OR']
    negation: bool
    children: List[Union[LogicStatement, LogicCombiner, sql_query.SubQuery]]

    def __init__(self, kind: Literal['AND', 'OR'], negation: bool, children: List[Union[LogicStatement, LogicCombiner]]) -> None:
        self.kind = kind
        self.negation = negation
        self.children = children
    
    def get_all_subqueries(self) -> List[sql_query.SubQuery]:
        subqueries = []
        for child in self.children:
            if isinstance(child, LogicCombiner):
                subqueries.extend(child.get_all_subqueries())
            elif isinstance(child, sql_query.SubQuery):
                subqueries.append(child)
        return subqueries

    def get_all_column_items(self) -> List[ColumnItem]:
        column_items = []
        logic_statements = self.get_all_logic_statments()
        for statement in logic_statements:
            if isinstance(statement.left_expression, ColumnItem):
                column_items.append(statement.left_expression)
        return column_items

    def get_all_logic_statments(self) -> List[LogicStatement]:
        logic_statements = []
        for child in self.children:
            if isinstance(child, LogicCombiner):
                logic_statements.extend(child.get_all_logic_statments())
            elif isinstance(child, LogicStatement):
                logic_statements.append(child)
        return logic_statements
    
    def __str__(self) -> str:
        children = self.children
        children = ',\n'.join([str(c) for c in self.children])
        return f'{self.kind}: [{children}]'
    
    def __repr__(self) -> str:
        return self.__str__()

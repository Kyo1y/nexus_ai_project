import logging

import re

from typing import List

from application.models.sql_query import logic_statement
from application.models.sql_query import parsing
from application.models.sql_query.column_item import ColumnItem

logger = logging.getLogger(__name__)

class WhereClause:
    orignal_text: str
    logic_steps: List[logic_statement.LogicCombiner]

    def __init__(self, text: str) -> None:
        self.orignal_text = text
        if text:
            self.logic_steps = WhereClause.process(text)
        else:
            self.logic_steps = []

    @staticmethod
    def process(text):
        return parsing.convert_logic_text(text)

    def get_all_subqueries(self):
        subqueries = []
        for logic_step in self.logic_steps:
            subqueries.extend(logic_step.get_all_subqueries())
        return subqueries

    def get_all_logic_statements(self) -> List[logic_statement.LogicStatement]:
        # logic_statements
        logic_statements = []
        for logic_step in self.logic_steps:
            logic_statements.extend(logic_step.get_all_logic_statments())
        return logic_statements

    def get_filters(self):
        filters = []
        for statement in self.get_all_logic_statements():
            filters.append((statement.left_expression, statement.operator, statement.right_expression))
        return filters

    @property
    def negation(self):
        return 'NOT' in self.orignal_text

import logging

from typing import List
from application.models.sql_query import logic_statement
from application.models.sql_query import parsing
from application.models.sql_query.column_item import ColumnItem

logger = logging.getLogger(__name__)

class HavingClause:
    original_text: str
    logic_steps: List[logic_statement.LogicCombiner]
    def __init__(self, having_text: str):
        self.original_text = having_text
        if having_text:
            self.logic_steps = HavingClause.process(having_text)
        else:
            self.logic_steps = []
        
    @staticmethod
    def process(text: str) -> List[logic_statement.LogicCombiner]:
        # TODO: Update typing
        return parsing.convert_logic_text(text)
    
    def get_all_logic_statements(self) -> List[logic_statement.LogicStatement]:
        # logic_statements
        logic_statements = []
        for logic_step in self.logic_steps:
            logic_statements.extend(logic_step.get_all_logic_statments())
        return logic_statements

    def get_filters(self):
        filters = []
        for statement in self.get_all_logic_statements():
            if isinstance(statement.left_expression, ColumnItem):
                col_item = statement.left_expression
                filters.append((col_item.field, col_item.func, statement.operator, statement.right_expression))
            else:
                logger.warning(f'Unable to convert {statement}')
        return filters

    
"""Contains logic for SQL Query and Sub Query. 

These classes. need to be kept together to avoid a circular import error.
"""
from __future__ import annotations
import re
import logging

from typing import List
from application.models import Value
from application.models.sql_query import date_parser
from application.models.sql_query import utils
from application.models.sql_query.select import SelectClause
from application.models.sql_query.having import HavingClause
from application.models.sql_query.where import WhereClause

logger = logging.getLogger(__name__)

class SQLQuery:
    original_text: str
    select: SelectClause
    from_clause: str
    where: WhereClause
    group_by: str
    having: HavingClause

    def __init__(self, query_text: str) -> None:
        self.original_text = self.validate(query_text)
        sql_mapping = SQLQuery.process(query_text) 

        if 'SELECT' in sql_mapping:
            self.select = SelectClause(sql_mapping['SELECT'])
        else:
            self.select = []

        if 'FROM' in sql_mapping:
            self.from_clause = sql_mapping['FROM']
        else:
            self.from_clause = None

        if 'WHERE' in sql_mapping:
            self.where = WhereClause(sql_mapping['WHERE'])
        else:
            self.where = WhereClause(None)

        if 'GROUP BY' in sql_mapping:
            self.group_by = sql_mapping['GROUP BY']
        else:
            self.group_by = None

        if 'HAVING' in sql_mapping:
            self.having = HavingClause(sql_mapping['HAVING'])
        else:
            self.having = HavingClause(None)

    def subqueries(self) -> List[SubQuery]:
        subqueries = []

        subqueries.extend(self.where.get_all_subqueries())
        # TODO: add for having and other clauses
        return subqueries


    def clean_sql_where_clause(self, sql_query: str) -> str:
        """Clean up WHERE clause of the SQL statement for `prim_ofcd` conditions, removing the clause if empty.
        
        Args:
            sql_query (str): The original SQL query.

        Returns:
            str: The modified SQL query without invalid `prim_ofcd` conditions or without a WHERE clause if it's empty.
        """
        # Regex to find and handle 'prim_ofcd' condition
        prim_ofcd_regex = r"(\s*AND\s+)?prim_ofcd\s*=\s*'([^']+)'(\s*AND\s+)?"
        
        # Split the query at 'WHERE' and handle no WHERE case
        parts = re.split(r"\bWHERE\b", sql_query, maxsplit=1)
        if len(parts) != 2:
            return sql_query  # No WHERE clause found, return the original query
        
        before_where, where_and_after = parts

        # Split the where_and_after to separate WHERE clause from other clauses
        where_parts = re.split(r"\b(GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT)\b", where_and_after, maxsplit=1, flags=re.IGNORECASE)
        
        # Process only the first part (the actual WHERE clause)
        actual_where_clause = where_parts[0]
        following_clauses = ''.join(where_parts[1:])  # Rejoin the rest of the query
        
        # Function to replace invalid 'prim_ofcd' conditions
        def replace_invalid_prim_ofcd(match):
            # Check if the captured 'prim_ofcd' value is a 3-character alphanumeric
            if re.fullmatch(r"[A-Za-z0-9]{3}", match.group(2)):
                return match.group(0)  # Valid condition, keep it
            # Adjust replacement to handle conjunctions correctly
            before_and = match.group(1) or ""
            after_and = match.group(3) or ""
            if before_and and after_and:
                return " AND "  # Both sides have AND, keep one
            else:
                return ""  # No valid 'prim_ofcd' condition, remove it entirely

        # Clean the WHERE clause
        cleaned_where_clause = re.sub(prim_ofcd_regex, replace_invalid_prim_ofcd, actual_where_clause).strip()

        # Remove any leading or trailing 'AND' and handle empty where clause
        cleaned_where_clause = re.sub(r"^\s*AND\s*|\s*AND\s*$", "", cleaned_where_clause, flags=re.IGNORECASE).strip()
        
        if not cleaned_where_clause:
            # If the cleaned WHERE clause is empty, return the query without the WHERE clause
            new_sql_query = before_where.strip() + " " + following_clauses.strip()
        else:
            # Otherwise, reassemble the query with the cleaned WHERE clause
            new_sql_query = before_where + "WHERE " + cleaned_where_clause + " " + following_clauses.strip()

        return new_sql_query.strip()
    
    
    def move_isdt_condition(self, query):
        # Define regex patterns
        not_in_pattern = re.compile(r'NOT IN\s*\(\s*SELECT\s+[^\)]+?\)', re.IGNORECASE)
        isdt_pattern = re.compile(r'AND\s+isdt\s*(>=|<=|>|<|=)\s*[^\s\)]+', re.IGNORECASE)
        
        # Find the NOT IN subquery
        not_in_match = not_in_pattern.search(query)
        if not_in_match:
            subquery = not_in_match.group()
            
            # Find the isdt condition in the subquery
            isdt_match = isdt_pattern.search(subquery)
            if isdt_match:
                isdt_condition = isdt_match.group()
                
                # Ensure the isdt condition is properly formatted without leading "AND "
                isdt_condition = isdt_condition.strip()
                
                # Insert isdt condition after the closing parenthesis of NOT IN clause
                insert_position = not_in_match.end()
                query = query[:insert_position] + ' ' + isdt_condition + query[insert_position:]
        
        return query

    
    def convert_datediff_to_julian(self, query):
        # Regular expression to find DATEDIFF statements
        datediff_pattern = re.compile(r'DATEDIFF\((YEAR|MONTH|DAY|QUARTER),\s*([^\s,]+),\s*([^\s,]+)\)', re.IGNORECASE)
        
        def replace_datediff(match):
            interval, start_date, end_date = match.groups()
            
            # Cast start_date and end_date to DATE if they are strings
            if re.match(r"'.*'", start_date):
                start_date = f"CAST({start_date} AS DATE)"
            if re.match(r"'.*'", end_date):
                end_date = f"CAST({end_date} AS DATE)"
            
            # Compute the interval in days
            if interval.upper() == 'YEAR':
                interval_days = '365.25'
            elif interval.upper() == 'MONTH':
                interval_days = '30.4375'  # Average number of days in a month
            elif interval.upper() == 'DAY':
                interval_days = '1'
            elif interval.upper() == 'QUARTER':
                interval_days = '91.31'  # Average number of days in a quarter
            
            # Replace with the new format
            return f"((julian({end_date}) - julian({start_date}))/{interval_days})"
        
        # Replace all occurrences of DATEDIFF in the query
        updated_query = datediff_pattern.sub(replace_datediff, query)
        
        return updated_query
    
    def ensure_order_by_name(self, query):
        try:
            # Pattern to match the SELECT clause
            select_pattern = re.compile(r'SELECT\s+(.+?)\s+FROM', re.IGNORECASE)
            select_match = select_pattern.search(query)

            # Check if 'name' is in the SELECT statement
            if select_match:
                select_columns = [col.strip() for col in select_match.group(1).split(',')]
                if 'name' in select_columns or any(col.endswith('name') for col in select_columns):
                    # Check if there is already an ORDER BY clause
                    order_by_pattern = re.compile(r'ORDER BY\s+(.+)', re.IGNORECASE)
                    order_by_match = order_by_pattern.search(query)

                    if order_by_match:
                        # Append 'name' to the existing ORDER BY clause
                        order_by_columns = [col.strip() for col in order_by_match.group(1).split(',')]
                        if 'name' not in order_by_columns:
                            order_by_columns.append('name')
                            new_order_by = "ORDER BY " + ', '.join(order_by_columns)
                            modified_query = re.sub(order_by_pattern, new_order_by, query)
                            return modified_query
                    else:
                        # Add a new ORDER BY clause
                        modified_query = query.strip() + " ORDER BY name"
                        return modified_query

            return query
        except Exception as e: 
            logger.exception("Unable to add ORDER BY clause due to the following exception: ", e)
            return query
    
    def add_supporting_columns(self, query):
        # Patterns to match the relevant parts of the query
        select_pattern = re.compile(r'SELECT\s+(.+?)\s+FROM', re.IGNORECASE)
        where_pattern = re.compile(r'WHERE\s+(.+?)(\s+GROUP BY|\s+HAVING|\s*$)', re.IGNORECASE)
        having_pattern = re.compile(r'HAVING\s+(.+?)(\s+ORDER BY|\s*$)', re.IGNORECASE)

        # Extract columns in the SELECT statement
        select_match = select_pattern.search(query)
        select_columns = []
        if select_match:
            select_columns = [col.strip().split(' ')[-1] for col in select_match.group(1).split(',')]

        # Extract columns in the WHERE clause with their comparison operators
        where_columns = []
        where_match = where_pattern.search(query)
        if where_match:
            where_columns = re.findall(r'(\w+)\s*(=|>|<|>=|<=|<>|BETWEEN|LIKE|IN)', where_match.group(1))

        # Extract columns in the HAVING clause with their comparison operators
        having_columns = []
        having_match = having_pattern.search(query)
        if having_match:
            having_columns = re.findall(r'(\w+)\s*(=|>|<|>=|<=|<>|BETWEEN|LIKE|IN)', having_match.group(1))

        # Combine WHERE and HAVING columns
        filtered_columns = set(where_columns + having_columns)

        # Ensure filtered columns are in SELECT statement
        columns_to_add = []
        for col, operator in filtered_columns:
            if col not in select_columns:
                if operator in ['>', '>=', 'BETWEEN']:
                    columns_to_add.append(f"MIN({col}) as minimum_{col}")
                elif operator in ['<', '<=']:
                    columns_to_add.append(f"MAX({col}) as maximum_{col}")

        if columns_to_add:
            # new_select = select_match.group(1) + ", " + ", ".join(columns_to_add)
            # modified_query = query.replace(select_match.group(1), new_select)
            new_select = select_match.group(1) + ", " + ", ".join(columns_to_add)
            # Replace only the SELECT clause by identifying its exact position
            start_index = select_match.start(1)
            end_index = select_match.end(1)
            modified_query = query[:start_index] + new_select + query[end_index:]
            return modified_query

        return query

    @staticmethod
    def ensure_select_group_by(query: str) -> str:
        def _is_sql_function(item):
            return re.match(r"\b\w+\s*\(", item, re.IGNORECASE)

        select_pattern = r"\bSELECT\b\s+(.*?)\bFROM\b"
        select_match = re.search(select_pattern, query, re.IGNORECASE | re.DOTALL)
        group_by_match = re.search(r"\bGROUP\s+BY\b\s+(.*)$", query, re.IGNORECASE | re.DOTALL)
        if not select_match or not group_by_match:
            return query

        select_clause = select_match.group(1).strip()
        select_items = [item.strip() for item in select_clause.split(",")]
        select_items_set = set([item.lower() for item in select_items])

        group_by_clause = group_by_match.group(1).strip()
        group_by_items = [item.strip() for item in group_by_clause.split(",")]

        for item in group_by_items:
            if re.search(r"\bname\b", item, re.IGNORECASE) and "name" not in select_items_set:
                for i, sel_item in enumerate(select_items):
                    if _is_sql_function(sel_item):
                        select_items.insert(i, "name")
                        break
                else:
                    select_items.append("name")

            if re.search(r"\bagent\b", item, re.IGNORECASE) and "agent" not in select_items_set:
                for i, sel_item in enumerate(select_items):
                    if _is_sql_function(sel_item):
                        select_items.insert(i, "agent")
                        break
                else:
                    select_items.append("agent")

        updated_select_clause = ", ".join(select_items)
        return re.sub(
            select_pattern, f"SELECT {updated_select_clause} FROM", query, flags=re.IGNORECASE | re.DOTALL,
        )

    def validate(self, query_text:str):
        input_str = date_parser.replace(query_text)
        where_clause_validated = self.clean_sql_where_clause(input_str)
        not_in_validated = self.move_isdt_condition(where_clause_validated)
        datediff_replaced = self.convert_datediff_to_julian(not_in_validated)
        order_by_name = self.ensure_order_by_name(datediff_replaced)
        supporting_columns = self.add_supporting_columns(order_by_name)
        select_group_by = self.ensure_select_group_by(supporting_columns)
        return select_group_by

    def has_negation(self):
        return self.where.negation

    def to_payload(self):
        agg_dict = {}
        for select_obj in self.select:
            agg = select_obj.agg_dict()
            if agg:
                agg_dict.update(agg)

        rev_agg_dict = {v:k for k,v in agg_dict.items()}
        # Check if need to add from having dict
        group_filters = []
        for having_obj in self.having:
            if (having_obj.field, having_obj.func) not in rev_agg_dict:
                agg_dict.update(having_obj.agg_dict())
            else:
                having_obj.name = rev_agg_dict[(having_obj.field, having_obj.func)]
            
            filterer = having_obj.create_filter()
            group_filters.append(filterer)
        
        if self.subqueries():
            subqueries = self.subqueries()
            for sub_query in subqueries:
                extra_selects = sub_query.query_obj.where.get_extra_select()
                for extra_select in extra_selects:
                    agg_dict.update(extra_select)

        agg_dict.update({f'count_pid': ('pid', 'count')})
        # if not agg_dict:
        #     if self.where:


        payload = {
            "filters": self.where.payload() if self.where else [],
            "grouping": {
                "by": self.group_by if self.group_by else 'agent',
                "agg_dict": agg_dict
            },
            "group_filters": [filterer.payload() for filterer in group_filters]
        }
        return payload

    @staticmethod
    def process(input_str: str):
        input_str = date_parser.replace(input_str)
        sql_chunks = chunk_sql_query(input_str)
        sql_mapping = validate_and_clean(sql_chunks)
        return sql_mapping


def split_str_on_indices(split_idxs: List[int], sql_query: str):
    chunks = []
    for i in range(len(split_idxs)-1):
        start = split_idxs[i]
        end = split_idxs[i+1]
        chunks.append(sql_query[start:end])
    return chunks

def chunk_sql_query(sql_query: str) -> List[str]:
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT']
    candidates = utils.find_split_candidates(sql_query, split_keywords=keywords)

    escaped_ranges = utils.find_matching_indices(sql_query)
    filterd_candidates = utils.filter_candidates(candidates, escaped_ranges)

    chunks = utils.convert_candidates_to_str_chunks(filterd_candidates, sql_query, remove_split_word=False)
    return chunks

def validate_and_clean(sql_chunks: List[str]):
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING']
    found = {keyword: 0 for keyword in keywords}
    chunk_mapping = {}
    for chunk in sql_chunks[::-1]:
        clean_chunk = chunk.strip()
        for keyword in keywords:
            if clean_chunk.startswith(keyword):
                chunk_mapping[keyword] = clean_chunk[len(keyword):].strip()
                found[keyword] += 1
    
    for key, count in found.items():
        if count > 1:
            print(f'Found {key} {count} times in, something is processing wrong')
    return chunk_mapping
    

# Basically child object of SQLQuery
class SubQuery:

    def __init__(self, text, field: str, operator: str, query: str) -> None:
        self.text = text
        self.field = field
        self.operator = operator.strip()
        self.query_text = re.sub(r'^\s*\((.*)\)\s*$', r'\1', query, flags=re.DOTALL).strip()

        self.query_obj = SQLQuery(self.query_text)

        self.filterer = None

    def convert(self, response_list: List[dict]):

        if self.operator in ['IN', 'NOT IN']:
            negate = 'NOT' in self.operator
            items = [resp[self.field] for resp in response_list]
            self.filterer = Value(self.field, items, negate)
        else:
            raise ValueError(f'Cannot handle type {self.operator} for operator')

    def payload(self):
        if self.filterer:
            return self.filterer.payload()
        else:
            raise ValueError(f'Cannot convert {self.__class__.__name__} to payload. Did you call convert() first to get filter object?')


    def __str__(self):
        return f'{self.__class__.__name__}(field={self.field}, operator={self.operator}, query={self.query_text})'
    def __repr__(self) -> str:
        return self.__str__()

if __name__ == '__main__':
    
    # sql_text = """
    #     SELECT agent, name
    #     FROM policy_data
    #     WHERE prim_ofcd = 'your office code'
    #     GROUP BY agent, name
    #     HAVING COUNT(DISTINCT source) = 1 AND MAX(source) = 'pending'
    # """
    # sql_text = """
    #     SELECT agent, name, MIN(famt) as min_famt, COUNT(pid) as policy_count
    #     FROM policy_data
    #     WHERE agent NOT IN (
    #         SELECT agent
    #         FROM policy_data
    #         WHERE famt < 100000 AND isdt > DATE_SUB('2024-05-30', INTERVAL 6 MONTH)
    #     )
    #     GROUP BY agent, name
    # """
    # sql_text = """
    #     SELECT agent, name, MAX(isdt)
    #     FROM policy_data
    #     WHERE prim_ofcd = 'B56' AND agent NOT IN (
    #         SELECT agent
    #         FROM policy_data
    #         WHERE isdt > DATE_SUB('2024-05-24', INTERVAL 8 MONTH)
    #     )
    #     GROUP BY agent, name
    # """

    # sql_text = """
    #     SELECT agent, name, MAX(isdt)
    #     FROM policy_data
    #     WHERE agent NOT IN (
    #         SELECT agent
    #         FROM policy_data
    #         WHERE isdt BETWEEN '2022-06-01' AND '2022-08-31'
    #     )
    #     GROUP BY agent, name
    # """

    # sql_text = """
    #     SELECT agent, name, MIN(famt) as min_famt, COUNT(pid) as policy_count
    #     FROM policy_data
    #     WHERE agent NOT IN (
    #         SELECT agent
    #         FROM policy_data
    #         WHERE famt < 100000 AND isdt > DATE_SUB('2024-05-24', INTERVAL 6 MONTH)
    #     )
    #     GROUP BY agent, name
    # """

    # sql_text = """
    #     SELECT agent, name, MIN(famt) as min_famt, COUNT(pid) as policy_count
    #     FROM policy_data
    #     WHERE agent NOT IN (
    #         SELECT agent
    #         FROM policy_data
    #         WHERE famt < 50000 AND isdt >= '2024-03-06'
    #     ) GROUP BY agent, name 
    # """

    sql_text = """
        SELECT agent, name, AVG(famt) as avg_famt, AVG(apamt) as avg_apamt, COUNT(pid)/DATEDIFF(YEAR, MIN(isdt), '2024-05-24') as avg_policy_per_year
        FROM policy_data
        WHERE prim_ofcd = 'B56'
        GROUP BY agent, name
        HAVING avg_famt > 100000 AND avg_apamt > 50 AND avg_policy_per_year >= 10
    """

    query = SQLQuery(sql_text)
    print(query.original_text)

    # import pandas as pd 
    # df = pd.read_csv('/Users/brapp/fp-assistant-chat/fp-assistant-chat/application/querier/test_examples_may24.csv')
    # for i, row in df.iterrows(): 
    #     print(i)
    #     sql_text = row['sql_statement']
    #     query = SQLQuery(sql_text)
    #     # print(query.original_text)
    #     df.at[i, 'validated_sql_statement'] = query.original_text

    # df.to_csv('/Users/brapp/fp-assistant-chat/fp-assistant-chat/application/querier/test_examples_may24.csv')
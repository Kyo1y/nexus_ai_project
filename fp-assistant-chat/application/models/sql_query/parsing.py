import re

from application.models.sql_query import sql_query 
from application.models.sql_query import utils
from application.models.sql_query.logic_statement import LogicStatement, LogicCombiner

from typing import List, Tuple, Union


def find_logic_escape_ranges(input_str: str) -> List[Tuple[int, int]]:
    # Find escape ranges, don't want to split inside.
    
    # Don't want to split inside of parenthesis, find indicies of them
    escaped_ranges = utils.find_matching_indices(input_str)
    # Need to check for BETWEEN ... AND to not split
    escaped_ranges += [(match.start(), match.end()) for match in re.finditer(r'BETWEEN.*?AND', input_str, re.IGNORECASE)]
    escaped_ranges = sorted(escaped_ranges)
    escaped_ranges = utils.merge_overlapping_ranges(escaped_ranges)
    return escaped_ranges




def find_logic_chunk(input_str: str) -> List[Tuple[str, List[str]]]:
    # Use baseline when no chunks to split on
    baseline = [('AND', [input_str])]
    
    candidates = utils.find_split_candidates(input_str, split_keywords=['AND\s*', 'OR\s*'])
    if not candidates:
        # No split candidates, return baseline
        return baseline
    escape_ranges = find_logic_escape_ranges(input_str)
    # Filter candidates that fall within escape ranges
    filterd_candidates = utils.filter_candidates(candidates, escape_ranges)
    if not filterd_candidates:
        return baseline
    
    # Build logic chunks based on candidate filtering
    operators = [filterd_candidates[0].text] + [candidate.text for candidate in filterd_candidates]
    chunks = utils.convert_candidates_to_str_chunks(filterd_candidates, input_str)
    grouped_chunks = utils.group_chunks_by_operators(operators, chunks)
    return grouped_chunks

def convert_logic_text(input_str: str):
    input_str = re.sub(r'^\s*\((.*)\)\s*$', r'\1', input_str)
    logic_chunks = find_logic_chunk(input_str)
    logic_container = []
    for chunk_kind, chunk_strs in logic_chunks:
        combiner_children = []
        for chunk in chunk_strs:
            child = process_logic_chunk(chunk)
            combiner_children.append(child)
        # TODO: fix negation False
        negation = input_str.lower().strip().startswith('not')
        combo = LogicCombiner(chunk_kind, negation, combiner_children)
        logic_container.append(combo)
    return logic_container

def extract_from_logic_structure(input_str: str):
    # Process single chunk
    operators = ['<=', '<', '=', '>', '>=', 'NOT IN', 'IN', 'LIKE','BETWEEN','!=', '<>']
    operator_pattern = '|'.join(operators)
    match = re.match(fr'(?P<left_expression>.*?)\s+?(?P<operator>{operator_pattern})\s+?(?P<right_expression>.*)', input_str, re.DOTALL)
    left_expression = match.group('left_expression').strip()
    operator = match.group('operator').strip()
    right_expression = match.group('right_expression').strip()
    return left_expression, operator, right_expression

def process_logic_chunk(chunk: str):
    if re.search(r'SELECT.*FROM', chunk, re.DOTALL):
        left_expression, operator, right_expression = extract_from_logic_structure(chunk)
        return sql_query.SubQuery(chunk, left_expression, operator, right_expression)

    elif 'OR' in chunk or (chunk.lower().count('between') != chunk.lower().count('and')):
        # More splits needed
        return convert_logic_text(chunk)

    else:
        left_expression, operator, right_expression = extract_from_logic_structure(chunk)
        return LogicStatement(chunk, left_expression, operator, right_expression)
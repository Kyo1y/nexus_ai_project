import functools
import re

import logging
import os

import numpy as np
import pandas as pd

from datetime import datetime
from typing import Dict, List, Tuple

from jinja2 import Environment, FileSystemLoader

from application.models import Agent, Response
from application.utils.datetime import str_to_datetime

current_dir = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader(os.path.join(current_dir, 'html_templates')))

logger = logging.getLogger(__name__)

def html_agent_table(response: Response) -> str:
    # Build table from agents
    if not response.results:
        return None
    df = build_data(response.results, response.dtypes)
    columns = df.columns.values
    data = df.values
    # Render template
    table_template = env.get_template('base_table.html')
    html_table = table_template.render(columns=columns, agents=data)
    return html_table

def str_agent_table(agents: List[Agent]) -> str:
    # Build table from agents
    df = build_data(agents)

    for col in df.columns:
        max_len = max(df[col].str.len().max(), len(col))
        df[col] = df[col].apply(lambda x: pad_string(x, max_len))
        df = df.rename(columns={col: pad_string(col, max_len)})
    

    rows = [' | '.join(df.columns)]
    rows.append('-' * len(rows[0]))
    for row in df.values:
        rows.append(' | '.join(row))
    
    return '\n'.join(rows)


def pad_string(orginal: str, amount: int, side='right'):
    if side == 'right':
        return orginal.rjust(amount)
    elif side == 'left':
        return orginal.ljust(amount)
    elif side == 'both':
        remainder = amount % 2
        half = amount // 2
        return orginal.rjust(half + remainder).ljust(half)

def sort_columns(col1: str, col2: str) -> int:
    if col1 == 'confidence':
        return 1
    elif col2 == 'confidence':
        return -1
    elif col1 == 'label':
        return 1
    elif col2 == 'label':
        return -1

    match1 = re.search(r'(.*?)_(.*)', col1)
    match2 = re.search(r'(.*?)_(.*)', col2)
    name_order = {name:i for i, name in enumerate(['volume', 'pid', 'famt', 'apamt', 'isdt'])}
    func_order = {name:i for i, name in enumerate(['count', 'min', 'mean', 'sum', 'max', 'previous', 'current'])}
    if match1 and match2:
        func1, name1 = match1.groups()
        func2, name2 = match2.groups()

        if name1 == name2:
            if func1 == func2:
                return 0
            elif func_order.get(func1, -1) > func_order.get(func2, -1):
                return 1
            else:
                return -1
        else:
            if name_order.get(name1, -1) > name_order.get(name2, -1):
                return 1
            else:
                return -1

    elif match1 and not match2:
        return 1
    elif not match1 and match2:
        return -1
    else:
        return 0

def unique_col(df: pd.DataFrame, col_name: str):
    return df.groupby(col_name).cumcount().add(1).astype(str).radd(df[col_name])

def unique_names(df: pd.DataFrame, unique_col: str, code_col: str):
    mask = df[unique_col].duplicated(keep=False)
    name_col = df[unique_col].copy()
    name_col[mask] = name_col[mask] + df[code_col].apply(lambda x: f' ({x})')
    return name_col


def build_data(agents: List[Agent], dtypes: Dict[str, str]) -> pd.DataFrame:
    if not agents:
        return None
    json_data = [agent.json() for agent in agents]
    df = pd.DataFrame(json_data)
    # Check for duplicate names and update
    new_names = unique_names(df, 'name', 'agent')
    df['name'] = new_names
    
    for column, col_type in dtypes.items():
        if column == 'agent':
            continue
        try:
            if col_type != 'object':
                df[column] = df[column].astype(col_type)
        except Exception as e:
            logger.exception(f'Failed to convert column "{column}" to "{col_type}". Error: {str(e)}')
    
    # Sort column names
    column_order = sorted(df.columns, key=functools.cmp_to_key(sort_columns))
    df = df[column_order]

    # Update column names
    column_mapping = {}
    col_names = {'famt': 'Face Amount', 'apamt': 'Annual Premiums', 'isdt': 'Policy Date', 'pid': 'Policies'}
    # old_mapping = {'previous_volume': 'Historical Average',
    #     'current_volume': 'Current Business Volume', 
    #     'historical_average_quarterly': 'Historical Average', 
    #     'current_volume_quarterly': 'Current Volume', 
    #     'avg_ratio_quarterly': 'Average Ratio',
    #     'max(isdt)':'Max Issued Date', 'min(isdt)':'Minimum Issued Date'}
    old_mapping = {
        'previous_volume': 'Historical Average',
        'current_volume': 'Current Business Volume', 
        'historical_average_quarterly': 'Historical Average', 
        'current_volume_quarterly': 'Current Volume',
        'avg_ratio_quarterly': 'Average Ratio',

        # agent
        'agent': 'Agent Code',
        'agentcode': 'Agent Code',
        'name': 'Agent Name',
        'status': 'Agent Status',

        # office
        'prim_ofcd': 'Primary Office Code',
        'primary_office_code': 'Primary Office Code',

        # issue date
        'min(isdt)': 'Minimum Issued Date',
        'max(isdt)': 'Maximum Issued Date',
        'Isdt': 'Issued Date',
        'minimum_issued_date': 'Minimum Issued Date',
        'maximum_issued_date': 'Maximum Issued Date',

        # annual premium
        'min(apamt)': 'Minimum Annual Premium',
        'max(apamt)': 'Maximum Annual Premium',
        'avg(apamt)': 'Average Annual Premium',
        'sum(apamt)': 'Total Annual Premium',
        'Apamt': 'Annual Premium',
        'minimum_annual_premium': 'Minimum Annual Premium',
        'maximum_annual_premium': 'Maximum Annual Premium',
        'total_annual_premium': 'Total Annual Premium',
        'average_annual_premium': 'Average Annual Premium',

        # face amount
        'min(famt)': 'Minimum Face Amount',
        'max(famt)': 'Maximum Face Amount',
        'avg(famt)': 'Average Face Amount',
        'sum(famt)': 'Total Face Amount',
        'Famt': 'Face Amount',
        'minimum_face_amount': 'Minimum Face Amount',
        'maximum_face_amount': 'Maximum Face Amount',
        'total_face_amount': 'Total Face Amount',
        'average_face_amount': 'Average Face Amount',

        # policy
        'count(pid)': 'Policy Count',
        'count(*)': 'Policy Count',
    }
    columns = df.columns
    for column in columns:
        if column in old_mapping or column.lower() in old_mapping:
            column_mapping[column] = old_mapping[column]
            continue
        else:
            # IF column alias
            if '_' in column:
                new_col_components = [c.capitalize() for c in column.split('_')]
                new_col_components = [old_mapping[c] if c in old_mapping.keys() else c for c in new_col_components]
                new_col = ' '.join(new_col_components)
                column_mapping[column] = new_col
            else:
                new_col = column.capitalize()
                column_mapping[column] = new_col
        
        # match = re.search(r'(.*?)_(.*)', column)
        # if match:
        #     func_name, col_name = match.groups()
        #     col_name = col_names.get(col_name, col_name)
        #     if func_name == 'count':
        #         func_name = 'count of'
        #     elif func_name == 'avg':
        #         func_name = 'Average'

        #     if '_' in col_name:
        #         col_name = ' '.join([c.capitalize() for c in col_name.split('_')])
        #     else:
        #         col_name = col_name.capitalize()

        #     column_mapping[column] = f'{func_name.capitalize()} {col_name}'
        # else:
        #     column_mapping[column] = column.capitalize()

    # Update columns with money values
    # dollar_keys = ['apamt', 'famt']
    # dollar_cols = [col for col in columns if any(dk in col for dk in dollar_keys)]
    dollar_search = '|'.join(['Face Amount', 'Premium', 'apamt', 'famt'])
    dollar_cols = [col for col in columns if re.search(fr'({dollar_search})', col, re.IGNORECASE)]
    for d_col in dollar_cols:
        df[d_col] = df[d_col].map('${:,.2f}'.format)

    # Update columns with date
    date_search = '|'.join(['Date', 'isdt'])
    date_cols = [col for col in columns if re.search(fr'({date_search})', col, re.IGNORECASE)]
    for d_col in date_cols:
        if pd.api.types.is_object_dtype(df[d_col]):
            df[d_col] = pd.to_datetime(df[d_col]).dt.strftime('%Y-%m-%d')
        else:
            df[d_col] = df[d_col].dt.strftime('%Y-%m-%d')
    
    # Add column with unique key so can be sorted in front-end
    df['key'] = unique_col(df, 'name')
    df = df.rename(columns=column_mapping)

    # Order columns
    return df

import json
import logging
import os
import time

import numpy as np
import pandas as pd
import requests

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

from app.data_manager.solr_query import Query
from app.data_manager.query_history import QueryHistory

from typing import List

from app.data_manager.solr_query import Query
from app.data_manager.query_history import QueryHistory
from app.data_manager.utils import normalize_column_names

AUTH_BASIC_TOKEN = 'UENTX1NWQzpQY3NQd2QxMjg='

DATE_TIME_FMT = '%Y-%m-%dT%H:%M:%SZ'

logger = logging.getLogger(__name__)

curr_dir = os.path.dirname(__file__)


def set_filter_date():
    current_datetime = datetime.utcnow()
    new_datetime = current_datetime - timedelta(hours=24)
    filter_date = new_datetime.strftime(DATE_TIME_FMT)
    return filter_date


def query_data(query: Query) -> pd.DataFrame:
    """
    Query data from a remote source using a Query object.

    Args:
        query (Query): An instance of the Query class containing query parameters.

    Returns:
        pd.DataFrame: A DataFrame containing the queried data.

    Notes:
        The function constructs a URL from the provided Query object, submits a GET request to the constructed
        URL, parses the response data into a pandas DataFrame, and returns the DataFrame. The function supports
        parsing JSON data and converting it into a DataFrame. For specific data structures or formats, additional
        processing may be required after parsing.
    """
    headers = {"Authorization": f"Basic {AUTH_BASIC_TOKEN}"}

    # Initial request
    response = requests.get(query.url(), headers=headers)
    if response.status_code == 200:
        
        response = requests.get(query.url(), headers=headers)
        json_data = json.loads(response.content)

        num_found = json_data['response']['numFound']
        if num_found > query.rows:
            logger.warning(f'More entries found than rows returned. There will be missing data. Found {num_found} but returning {query.rows}. URL: {query.url()}')

        df = pd.DataFrame(json_data['response']['docs'])

        return df
    else:
        logger.error(f'Failed URL: {response.url}')
        response.raise_for_status()


def store_data(df: pd.DataFrame, data_kind: str, store_method: str):
    """
    Store data to a local CSV file or a DynamoDB table.

    Args:
        df (pd.DataFrame): A DataFrame containing the data to be stored.
        data_kind (str): Specifies the type of data being stored ('PCS' or 'FCS').
        store_method (str): Specifies the storage method ('CSV' or 'DynamoDB').

    Raises:
        ValueError: If the specified store method is invalid.

    Notes:
        The function takes a DataFrame containing PCS or FCS data and stores it accordingly. For CSV storage,
        the data is appended to an existing CSV file or created if the file does not exist. Duplicate entries
        are handled by dropping duplicates based on specific columns. For DynamoDB storage, the functionality
        is not implemented yet.
    """
    if store_method.lower() == 'csv':
        file_path = os.path.join(curr_dir, 'agents', f'{data_kind.lower()}_data.csv')
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            if data_kind.lower() == 'pcs':
                df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset='pid', keep='last')
            elif data_kind.lower() == 'fcs':
                df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset='prim_agcd', keep='last')
        df.to_csv(file_path, index=False)
    elif store_method.lower() == 'dynamodb':
        # Implement DynamoDB storing functionality
        raise NotImplementedError("DynamoDB storage option is not implemented yet")
    else:
        raise ValueError("Invalid store method. Must be 'csv' or 'dynamodb'.")


def load_local_data(load_params: list, data_kind: str, load_method: str) -> pd.DataFrame:
    """
    Load data from a local CSV file or a DynamoDB table.

    Args:
        load_params (list): A list of column names to filter the loaded DataFrame.
        data_kind (str): Specifies the type of data to load ('PCS' or 'FCS').
        load_method (str): Specifies the loading method ('CSV' or 'DynamoDB').

    Returns:
        pd.DataFrame: A DataFrame containing the loaded data.

    Raises:
        ValueError: If the specified load method is invalid.

    Notes:
        For CSV loading, the function reads data from a local CSV file located in the 'agents' directory.
        If the file exists, it loads the data into a DataFrame and applies filtering based on the provided
        load parameters. For columns containing serialized data like lists, appropriate conversion methods
        should be applied manually.
    """
    if load_method.lower() == 'csv':
        file_path = os.path.join(curr_dir, 'agents', f'{data_kind.lower()}_data.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if load_params:
                df = df[load_params]
            # handle agcds in pcs: If 'agcds' column needs to be converted back to a list of strings
            if 'agcds' in df.columns:
                df['agcds'] = df['agcds'].apply(eval)
            return df
        else:
            print(f"File '{file_path}' not found. Returning an empty DataFrame.")
            return pd.DataFrame()  # Return an empty DataFrame if the file does not exist
    elif load_method == 'DynamoDB':
        # Implement DynamoDB loading functionality
        raise NotImplementedError("DynamoDB storage option is not implemented yet")
    else:
        raise ValueError("Invalid load method. Must be 'CSV' or 'DynamoDB'.")


def get_pcs_data(agent_codes: List[str], query_history: QueryHistory, agent_chunk_n: int = 25, force: bool = False, skip_update: bool = False, query_recent: bool = True) -> pd.DataFrame:
    """
    Retrieve PCS data based on the provided agent codes and optional filter date.

    Arguments:
        agent_codes (List[str]): A list of agent codes to query PCS data.
        filter_date (Optional[str]): An optional filter date to restrict data retrieval.

    Returns:
        pd.DataFrame: A DataFrame containing PCS data.

    Notes:
        This function constructs a query object based on the provided agent codes and filter date, queries data from a
        remote source, stores the retrieved data locally, and loads it into a DataFrame. The loaded data is returned
        for further processing. The function primarily deals with querying and managing PCS data.
    """
    

    if not skip_update and (query_history.PCS.ready_to_run() or force):
        if query_recent:
            # Get last ran to filter on
            filter_date = query_history.PCS.last_run_str
            fq = f'mddt:[{filter_date} TO NOW]' if filter_date else None
        else:
            fq = None

        agent_codes = [code for code in agent_codes if not pd.isna(code)]
        for i in range(0, len(agent_codes), agent_chunk_n):
            print(i, (i + agent_chunk_n))
            codes_fmt = f'({"%20OR%20".join(agent_codes[i:(i+agent_chunk_n)])})'

            pcs_query = Query(base_url='http://pcs.pennmutual.com/pcs-ws/system/search',
                            q=f'agcds:{codes_fmt}',
                            fq=fq,
                            fl='agcds,pid,source,isdt,mddt,edt,edtmn,edtyr,famt,puwamt,pamt,apamt,mdpremamt,totannpremamt',
                            wt='json', rows=10000, decrypt=True, start=0)
            if i == 0:
                df = query_data(pcs_query)
            else:
                df = pd.concat([df, query_data(pcs_query)], ignore_index=True)

        store_data(df, 'pcs', 'csv')
        query_history.PCS.ran()
        query_history.save()
    else:
        logger.info('Skipping call to data endpoints, just loading')
    
    pcs_df = load_local_data([], 'pcs', 'csv')

    return pcs_df


def get_fcs_data(office_code: str, query_history:QueryHistory, force: bool = False, skip_update: bool = False, query_recent: bool = True) -> pd.DataFrame:
    """Retrieve FCS data based on predefined criteria.

    The function constructs a Query object based on predefined criteria, queries data from a remote source,
    stores the retrieved data locally, and loads it into a DataFrame. The loaded data is returned for further
    processing. The function primarily deals with querying and managing FCS data.

    Args:
        office_code (str): first line office code
        query_history (QueryHistory): object with records of running
        force (bool, optional): force to refresh data. Defaults to False.
        skip_update (bool, optional): skip updating the data and just load. Default is False
        query_recent (bool, optional): use last run date to filter records. When False, will take longer to run. Default is True

    Returns:
        pd.DataFrame: A DataFrame containing FCS data.
    """
    if not skip_update and (query_history.FCS.ready_to_run() or force):
        
        if query_recent:
            # Get last ran to filter on
            filter_date = query_history.FCS.last_run_str
            fq = f'mddt:[{filter_date} TO NOW]' if filter_date else None
        else:
            fq = None

        fcs_query = Query(base_url='http://fcs-ws.pennmutual.com/fcs-ws/system/search',
            q=f'active:true AND ptyp:Person AND flofcd:{office_code}',
            fq=fq,
            fl='prim_agcd,nm, actst,ofcds,prim_ofcd,flofcd,ocdfn,roles,'
                'ofcds,actagcds,flofcd,flofnm,porgcd,mddt,hrdt,strdt,strind,mstrind,eliteind',
            wt='json', rows=10000, decrypt=True, start=0)

        df = query_data(fcs_query)

        # Filter out inactive agents
        df = df[(df['actst'] != '') & (~df['actst'].isna())]
        

        store_data(df, 'fcs', 'csv')
        # Update history object
        query_history.FCS.ran()
        query_history.save()
    else:
        logger.info('Skipping call to data endpoints, just loading')


    fcs_df = load_local_data(['prim_agcd', 'nm', 'prim_ofcd', 'strdt'], 'fcs', 'csv')

    return fcs_df

def map_agent_status_to_agent_code(results_df):

    # Load in FCS 
    data_dir = os.path.join(curr_dir, 'agents')
    fcs_path=os.path.join(data_dir, 'fcs.txt')
    fcs_df = pd.read_csv(fcs_path, delimiter='|')

    # Create column for agent status
    resulting_df = results_df.merge(fcs_df[['Prim_agcd', 'Status']], left_on='agent', right_on='Prim_agcd', how='left')
    resulting_df.drop('Prim_agcd', axis=1, inplace=True)
    resulting_df.rename({'Status':'status'}, axis=1, inplace=True)

    return resulting_df


def filter_active_agents(pcs_df, fcs_df):

    date_2_years_ago = datetime.now().replace(year=datetime.now().year - 2)

    pcs_df['isdt'] = pd.to_datetime(pcs_df['isdt'])
    most_recent_policy_by_agent = pcs_df[['isdt', 'agcds']].groupby('agcds').agg(max)
    filtered_by_recency = most_recent_policy_by_agent[most_recent_policy_by_agent['isdt'] > date_2_years_ago].reset_index()
    fcs_recent_agents = fcs_df[fcs_df['actagcds'].isin(set(filtered_by_recency['agcds']))]

    return fcs_recent_agents


def static_collect(fcs_path: str, pcs_path: str, office_code: str = '520') -> pd.DataFrame:
    fcs_df = pd.read_csv(fcs_path, delimiter="|")
    pcs_df = pd.read_csv(pcs_path)
    normalize_column_names(fcs_df)
    normalize_column_names(pcs_df)
    
    
    fcs_df = fcs_df.loc[(fcs_df['flofcd'] == office_code) & ~(fcs_df['prim_agcd'].isna())]
    fcs_df['actagcds'] = fcs_df['actagcds'].str.split(';')
    fcs_df = fcs_df.explode('actagcds')
    fcs_df = fcs_df[~fcs_df['actagcds'].isna()]
    # fcs_df = filter_active_agents(pcs_df, fcs_df) # Currently just picking agents who have written a policy in the last 2 years

    fcs_active_agent_code_to_primary_agent_code = dict(zip(fcs_df['actagcds'].tolist(), fcs_df['prim_agcd'].tolist()))
    fcs_active_agent_code_to_name = dict(zip(fcs_df['actagcds'].tolist(), fcs_df['nm'].tolist()))
    fcs_active_agent_code_to_office_code = dict(zip(fcs_df['actagcds'].tolist(), fcs_df['prim_ofcd'].tolist()))


    pcs_df = pcs_df[~pcs_df['agcds'].isna()]
    pcs_df['name'] = pcs_df['agcds'].map(fcs_active_agent_code_to_name)
    pcs_df['prim_ofcd'] = pcs_df['agcds'].map(fcs_active_agent_code_to_office_code)
    pcs_df.dropna(subset=['name'], inplace=True)
    pcs_df.rename(columns={'agcds': 'agentcode'}, inplace=True)
    pcs_df['agent'] = pcs_df['agentcode']

    pcs_active_agent_to_start_date = dict(zip(fcs_df['actagcds'].tolist(), fcs_df['strdt'].tolist()))
    pcs_df['strdt'] = pcs_df['agent'].map(pcs_active_agent_to_start_date)
    pcs_df['agent'] = pcs_df['agent'].map(fcs_active_agent_code_to_primary_agent_code)

    pcs_df.isdt = pd.to_datetime(pcs_df.isdt)
    final_df = pcs_df.sort_values(by='isdt').drop_duplicates(['pid'], keep='last')

    final_df = final_df[['pid', 'apamt', 'isdt', 'famt', 'source', 'name', 'prim_ofcd', 'agent', 'strdt']]

    return final_df


def collect() -> pd.DataFrame:
    data_dir = os.path.join(curr_dir, 'agents')
    return static_collect(fcs_path=os.path.join(data_dir, 'fcs.txt'), pcs_path=os.path.join(data_dir, 'pcs_deduped.csv'))


if __name__ == "__main__":

    # # STEP 1: Get the QC agent codes, format as list 
    # qc_agents = ['95194']

    # # STEP 2: Make sure query history is set up 
    # query_history = QueryHistory(run_interval=relativedelta(days=1))

    # # STEP 3: Debug through run_pcs_data(qc_agents, query_history) 
    # get_pcs_data(qc_agents, query_history)

    df = collect()
    print(df.columns)

import json
import logging
import os
import re

import pandas as pd
import requests

from abc import ABC, abstractmethod
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Any, Dict, List, Tuple, Union, get_args, get_origin

from application.models import Agent
from application.models import Query
from application.models import QueryType, PerformanceVolumeType
from application.models import Response
from application.requestor import payload
from application.models import SQLQuery
from application.models import Range, Value
from application.models import Query, Response, Assumptions, Period

logger = logging.getLogger(__name__)

class Connector(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """Configure connection.
        """
        super().__init__()

    @abstractmethod
    def process(self, query: Query) -> Response: pass

class JSONMockConnector(Connector):
    data_path: str
    data: List[Dict[str, Any]]
    def __init__(self) -> None:
        """Dummy class to test building data from JSON file `mock_data/agents.json`"""
        file_name = 'agents.json'

        self.data_path = os.path.join(os.path.dirname(__file__), 'mock_data', file_name)
        self.historical_key = 'Historical Avg'
        self.current_key = 'Current Volume'
        self.name_key = 'FullName'
        
        with open(self.data_path, 'r') as json_file: 
            self.data = json.load(json_file)

    def process(self, query: Query) -> Response:
        logger.warning(f'Using JSONMockConnector to get data. Update to actual data source')
        return super().process(query)

    def process_both(self, query: Query) -> Response:
        agents = []
        for entry in self.data:
            if entry[self.current_key] > entry[self.historical_key] or entry[self.current_key] < entry[self.historical_key]:
                agent = self.__convert_json_to_agent(entry)
                agents.append(agent)

        response = Response(query=query, results=agents)
        return response

    def process_high(self, query: Query) -> Response:
        agents = []
        for entry in self.data:
            if entry[self.current_key] > entry[self.historical_key]:
                agent = self.__convert_json_to_agent(entry)
                agents.append(agent)

        response = Response(query=query, results=agents)
        return response
    
    def process_low(self, query: Query) -> Response:
        agents = []
        for entry in self.data:
            if entry[self.current_key] < entry[self.historical_key]:
                agent = self.__convert_json_to_agent(entry)
                agents.append(agent)

        response = Response(query=query, results=agents)
        return response

    def __convert_json_to_agent(self, entry: Dict[str, Any]) -> Agent:
        agent = Agent(name=entry[self.name_key], previous_performance=entry[self.historical_key], 
                        current_performance=entry[self.current_key])
        return agent

class JSONMockConnectorV2(Connector):
    data_path: str
    data: List[Dict[str, Any]]
    def __init__(self) -> None: 
        file_name = 'agents_v2.json'

        self.data_path = os.path.join(os.path.dirname(__file__), 'mock_data', file_name)
        self.historical_key = 'historical_average'
        self.current_key = 'current_volume'
        self.name_key = 'agent_name'
        
        with open(self.data_path, 'r') as json_file: 
            self.data = json.load(json_file)

    def process(self, query: Query) -> Response:
        logger.warning(f'Using JSONMockConnectorV2 to get data. Update to actual data source')
        return super().process(query)

    def process_both(self, query: Query) -> Response:
        agents = []
        for entry in self.data['abnormally_high'] + self.data['abnormally_low']:

            agent = self.__convert_json_to_agent(entry)
            agents.append(agent)

        response = Response(query=query, results=agents)
        return response

    def process_high(self, query: Query) -> Response:
        agents = []
        for entry in self.data['abnormally_high']:
            agent = self.__convert_json_to_agent(entry)
            agents.append(agent)

        response = Response(query=query, results=agents)
        return response
    
    def process_low(self, query: Query) -> Response:
        agents = []
        for entry in self.data['abnormally_low']:

            agent = self.__convert_json_to_agent(entry)
            agents.append(agent)

        response = Response(query=query, results=agents)
        return response

    def __convert_json_to_agent(self, entry: Dict[str, Any]) -> Agent:
        agent = Agent(name=entry[self.name_key], previous_performance=entry[self.historical_key], 
                        current_performance=entry[self.current_key])
        return agent

class CSVMockConnector(Connector):
    summarized: pd.DataFrame
    agent_data: pd.DataFrame
    def __init__(self) -> None:
        super().__init__()
        data_path = os.path.join(os.path.dirname(__file__), 'mock_data', '520-MichaelKane.csv')
        self.summarized = pd.read_csv(data_path)
        self.agent_data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'mock_data', 'agents_table.csv'))
        self.agent_data['isdt'] = pd.to_datetime(self.agent_data['isdt']).dt.date

    def process(self, query: Query) -> Response:
        logger.warning(f'Using CSVMockConnector to get data. Update to actual data source')
        if isinstance(query, Query.performance):
            # Handle Performance Queries
            # TODO: Simplify this logic
            if query.query_type == PerformanceVolumeType.HIGH:
                return self.process_high(query)
            elif query.query_type == PerformanceVolumeType.LOW:
                return self.process_low(query)
            elif query.query_type == PerformanceVolumeType.BOTH:
                return self.process_both(query)
        elif isinstance(query, (Query.not_written, Query.agent_amount)):
            return self.process_agent_question(query)

        else:
            raise ValueError(f'Cannot process query type: {query}, need to configure in Connector.')

    def process_agent_question(self, query: Union[Query.not_written, Query.agent_amount]) -> Response: 
        if isinstance(query, Query.agent_amount):
            df = self.agent_data.loc[(self.agent_data['isdt'] > query.date.date())]
            df = df.groupby(['AgentCode', 'Name'], as_index=False)['famt'].max()
            df = df[df['famt'] > query.amount]
            json_data = df.to_dict(orient='records')
            agents = APIConnector.convert_json_to_agent(json_data)
            response = Response(query=query, results=agents)
            return response

        elif isinstance(query, Query.not_written):
            df = self.agent_data.loc[self.agent_data['source'] == 'inforce']
            df = df.sort_values(by="isdt").drop_duplicates(['AgentCode', 'Name'], keep="last")
            df = df[['AgentCode','Name','isdt']]
            df = df.loc[(df['isdt'] < query.date.date())]
            json_data = df.to_dict(orient='records')
            agents = APIConnector.convert_json_to_agent(json_data)
            response = Response(query=query, results=agents)
            return response


    def process_both(self, query: Query) -> Response:
        # Filter data frame for relevant rows
        filter_mask = (self.summarized['Current Volume'] > self.summarized['Historical Avg']) | (self.summarized['Current Volume'] < self.summarized['Historical Avg'])
        subset = self.summarized[filter_mask]
        agents = self.__convert_df_to_agents(subset)
        response = Response(query=query, results=agents)
        return response
    
    def process_high(self, query: Query) -> Response:
        # Filter data frame for relevant rows
        filter_mask = self.summarized['Current Volume'] > self.summarized['Historical Avg']
        subset = self.summarized[filter_mask]
        agents = self.__convert_df_to_agents(subset)
        response = Response(query=query, results=agents)
        return response

    def process_low(self, query: Query) -> Response:
        # Filter data frame for relevant rows
        filter_mask = self.summarized['Current Volume'] < self.summarized['Historical Avg']
        subset = self.summarized[filter_mask]
        agents = self.__convert_df_to_agents(subset)
        response = Response(query=query, results=agents)
        return response
    
    def __convert_df_to_agents(self, subset: pd.DataFrame) -> List[Agent]:
        agents = []
        for row_idx, row_data in subset.iterrows():
            agent_name = row_data['FullName']

            agent = Agent(name=agent_name, previous_performance=row_data['Historical Avg'], current_performance=row_data['Current Volume'])
            agents.append(agent)
        return agents


class XLSXMockConnector(Connector):
    def __init__(self) -> None:
        data_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'API-step1-2Years-flofcd-520.xlsx')
        self.full_data_frame = pd.read_excel(data_path, 'ConsolidatedMonthly')
        self.summarized = XLSXMockConnector.__process_xlsx(self.full_data_frame)
        self.code2name = XLSXMockConnector.__get_code_to_agent(data_path)

    def process(self, query: Query) -> Response:
        logger.warning(f'Using XLSXMockConnector to get data. Update to actual data source')
        return super().process(query)

    def process_both(self, query: Query) -> Response:
        # Filter data frame for relevant rows
        filter_mask = (self.summarized['current'] > self.summarized['mean']) | (self.summarized['current'] < self.summarized['mean'])
        subset = self.summarized[filter_mask]
        agents = self.__convert_df_to_agents(subset)
        response = Response(query=query, results=agents)
        return response
    
    def process_high(self, query: Query) -> Response:
        # Filter data frame for relevant rows
        filter_mask = self.summarized['current'] > self.summarized['mean']
        subset = self.summarized[filter_mask]
        agents = self.__convert_df_to_agents(subset)
        response = Response(query=query, results=agents)
        return response

    def process_low(self, query: Query) -> Response:
        # Filter data frame for relevant rows
        filter_mask = self.summarized['current'] < self.summarized['mean']
        subset = self.summarized[filter_mask]
        agents = self.__convert_df_to_agents(subset)
        response = Response(query=query, results=agents)
        return response

    @staticmethod
    def __get_code_to_agent(data_path):
        data_frame = pd.read_excel(data_path, 'Sheet1')
        code2name = pd.Series(data_frame['FullName'].values, index=data_frame['PrimaryAgentCode']).to_dict()
        return code2name

    def __convert_df_to_agents(self, subset: pd.DataFrame) -> List[Agent]:
        agents = []
        for row_idx, row_data in subset.iterrows():
            agent_code = row_data['Agent Code']
            agent_name = self.code2name.get(agent_code, agent_code)

            agent = Agent(name=agent_name, previous_performance=row_data['mean'], current_performance=row_data['current'])
            agents.append(agent)
        return agents

    @staticmethod
    def __process_xlsx(data_frame: pd.DataFrame) -> pd.DataFrame:

        # Assumption: Agent Code only column not needed in response
        avg_columns = [c for c in data_frame.columns if c not in ['Agent Code']]
        data_frame = data_frame.dropna(subset=avg_columns, how='all').copy()
        # Assuming NA should be 0 and not ignored
        data_frame = data_frame.fillna(0)
        data_frame['mean'] = data_frame[avg_columns].mean(axis='columns')
        data_frame['current'] = data_frame[avg_columns[-1]]
        subset = data_frame[['Agent Code', 'mean', 'current']]
        return subset


class APIConnector(Connector):
    def __init__(self, base_url) -> None:
        self.base_url = base_url
    pass

    # TODO: Set up query object to include endpoint and conversion to payload
    def process(self, query: Query): 
        if isinstance(query, Query.performance):
            # Handle Performance Queries
            return self.process_performance(query)
        elif isinstance(query, SQLQuery):
            return self.process_sql_direct(query)
        elif isinstance(query, (Query.not_written, Query.agent_amount)):
            return self.process_agent_query(query)
        else:
            raise ValueError(f'Cannot process query type: {query}, need to configure in Connector.')

    def process_sql(self, query: SQLQuery) -> Response:

        # Need to resolve any subqueries first

        subqueries = query.subqueries()
        if subqueries:
            identity = query.identity
            for sub_query in subqueries:

                sub_query_obj = sub_query.query_obj
                sub_query_obj.identity = identity
                payload = APIConnector.convert_sql_to_payload(sub_query_obj)
                endpoint = os.path.join(self.base_url, 'query')
                api_response = APIConnector.post_request(endpoint, payload)

                # Will be able to filter on object now
                sub_query.convert(api_response['agent_list'])


        payload = APIConnector.convert_sql_to_payload(query)
        endpoint = os.path.join(self.base_url, 'query')
        api_response = APIConnector.post_request(endpoint, payload)
        if api_response:
            agents = APIConnector.convert_json_to_agent(api_response['agent_list'])
            agents = sorted(agents, key=lambda x: (x.name.split(' ')[-1]))
            dtypes = api_response['dtypes']
            response = Response(query=query, results=agents, dtypes=dtypes)
        else:
            response = Response(query=query, metadata={'error': 'failed to get data'}, results=[])
        return response

    def process_sql_direct(self, query: SQLQuery):
        sql_query = query.original_text
        endpoint = os.path.join(self.base_url, 'sql')
        payload = {'query': sql_query}
        api_response = APIConnector.post_request(endpoint, payload)
        if api_response:
            agents = APIConnector.convert_json_to_agent(api_response['agent_list'])
            agents = sorted(agents, key=lambda x: (x.name.split(' ')[-1]))
            dtypes = api_response['dtypes']
            response = Response(query=query, results=agents, dtypes=dtypes)
        else:
            response = Response(query=query, metadata={'error': 'failed to get data'}, results=[])
        return response

    def process_agent_query(self, query: Union[Query.not_written, Query.agent_amount]):
        payload = query.build_payload()
        endpoint = os.path.join(self.base_url, 'query')
        api_response = APIConnector.post_request(endpoint, payload)
        if api_response:
            agents = APIConnector.convert_json_to_agent(api_response['agent_list'])
            agents = sorted(agents, key=lambda x: (x.name.split(' ')[-1]))
            response = Response(query=query, results=agents)
        else:
            response = Response(query=query, metadata={'error': 'failed to get data'}, results=[])
        return response

    def process_agent_amount(self, query: Query.agent_amount):
        time_delta = datetime.now() - query.date_value

        payload = {
            "name": "over_amount",
            "filter": [
                {
                    "key": "famt",
                    "operator": "greater",
                    "value": query.amount_value
                }
            ],
            "period": {
                "unit": "days",
                "value": time_delta.days
            }
        }

        endpoint = os.path.join(self.base_url, 'agent-count')
        api_response = APIConnector.post_request(endpoint, payload)
        if api_response:
            agents = APIConnector.convert_json_to_agent(api_response['agent_list'])
            agents = sorted(agents, key=lambda x: (x.name.split(' ')[-1]))
            response = Response(query=query, results=agents)
        else:
            response = Response(query=query, metadata={'error': 'failed to get data'}, results=[])
        return response
        

    def process_not_written(self, query: Query.not_written):
        time_delta =  datetime.now() - query.date

        payload = {
            "name": "not_written",
            "filter": [],
            "period": {
                "unit": "days",
                "value": time_delta.days
            }
        }

        endpoint = os.path.join(self.base_url, 'agent-count')
        api_response = APIConnector.post_request(endpoint, payload)
        agents = APIConnector.convert_json_to_agent(api_response['agent_list'])
        agents = sorted(agents, key=lambda x: (x.name))
        response = Response(query=query, results=agents)
        return response

    def process_performance(self, query: Query.performance, use_start=True):
        # TODO: Update to change period to user parameter
        
        unit = "months"
        value = 12
        end_date = datetime.now() - relativedelta(months=1)
        frequency = "monthly"
        if use_start and query.period and query.period.start:
            start_date = query.period.start
        else:
            start_date = end_date - relativedelta(months=value)

        period = Period(start=start_date, end=end_date, frequency=frequency)
        assumptions = Assumptions(period)
        query.assumptions = assumptions

        payload = {
            "name": "agent_analysis",
            "period": {
                "unit" : unit,
                "value": value,
                "frequency": frequency
            }
        }
        endpoint = os.path.join(self.base_url, 'agent/gpt/analysis')
        api_response = APIConnector.post_request(endpoint, payload)
        if api_response:
            agents = APIConnector.convert_json_to_agent(api_response)
            # Filter out based on request. May want to do this elsewhere
            if query.volume == PerformanceVolumeType.LOW:
                agents = [agent for agent in agents if agent.label == 'low']
            elif query.volume == PerformanceVolumeType.HIGH:
                agents = [agent for agent in agents if agent.label == 'high']
            elif query.volume == PerformanceVolumeType.BOTH:
                agents = [agent for agent in agents if agent.label in ['high', 'low']]
            
            agents = sorted(agents, key=lambda x: (x.label, *x.name.split(' ')[::-1]))
            response = Response(query=query, results=agents)
        else:
            response = Response(query=query, metadata={'error': 'failed to get data'}, results=[])
        return response

    def process_performance_v2(self, query: Query.performance):
        endpoint = os.path.join(self.base_url, 'agent/gpt/analysis')
        
        payload = query.build_payload()
        api_response = APIConnector.post_request(endpoint, payload)
        if api_response:
            agents = APIConnector.convert_json_to_agent(api_response)
            # Filter out based on request. May want to do this elsewhere
            if query.volume == PerformanceVolumeType.LOW:
                agents = [agent for agent in agents if agent.label == 'low']
            elif query.volume == PerformanceVolumeType.HIGH:
                agents = [agent for agent in agents if agent.label == 'high']
            elif query.volume == PerformanceVolumeType.BOTH:
                agents = [agent for agent in agents if agent.label in ['high', 'low']]
            
            agents = sorted(agents, key=lambda x: (x.label, *x.name.split(' ')[::-1]))
            response = Response(query=query, results=agents)
        else:
            response = Response(query=query, metadata={'error': 'failed to get data'}, results=[])
        return response
        return 

    @staticmethod
    def convert_name(field: str, func: str) -> str:
        func_coverter = {'avg': 'mean'}
        field_converter = {'*': 'pid'}  # Set to pid for wildcard

        func_name = func.lower()
        field = field.lower()

        func_name = func_coverter.get(func_name, func_name)
        field = field_converter.get(field, field)

        agg_name = f'{func_name}_{field}'
        return agg_name

    @staticmethod
    def convert_select_items(select_items: List[Tuple[str, str]]):
        agg_dict = {}
        func_coverter = {'avg': 'mean'}
        for field, func_name in select_items:
            if func_name:
                agg_name = APIConnector.convert_name(field, func_name)
                func_name = func_coverter.get(func_name.lower(), func_name.lower())
                agg_dict[agg_name] = (field, func_name)
        return agg_dict

    @staticmethod
    def convert_sql_to_payload(query_obj: SQLQuery):
        # Create payload
        func_coverter = {'avg': 'mean'}
        agg_dict = APIConnector.convert_select_items(query_obj.select.get_field_funcs())

        having_filters = query_obj.having.get_filters()
        group_filters = []
        for having_filter in having_filters:
            field, func, operator, value = having_filter

            agg_name = APIConnector.convert_name(field, func)
            func = func_coverter.get(func.lower(), func.lower())
            agg_dict[agg_name] = (field.lower(), func.lower())
            filterer = APIConnector.convert_to_filter(agg_name, operator, value).payload()
            group_filters.append(filterer)

        filters = []
        where_filters = query_obj.where.get_filters()
        for where_filter in where_filters:
            field, operator, value = where_filter
            filterer = APIConnector.convert_to_filter(field, operator, value).payload()
            filters.append(filterer)

        # Add in from SubQueries
        if query_obj.subqueries():
            subqueries = query_obj.where.get_all_subqueries()
            for subquery in subqueries:
                try:
                    filters.append(subquery.payload())
                except:
                    logger.exception(f'Failed to get payload for subquery {subquery}')

        if not agg_dict:
            agg_dict.update({f'count_pid': ('pid', 'count')})

        payload = {
            "filters": filters,
            "grouping": {
                "by": query_obj.group_by if query_obj.group_by else 'agent',
                "agg_dict": agg_dict
            },
            "group_filters": group_filters,
            "identity": query_obj.identity
        }
        return payload

    @staticmethod
    def convert_to_filter(name, operator, value: str):
        if operator in ['BETWEEN']:
            value = re.sub(r'[\'"]', '', value)
            lower, upper = [v.strip() for v in value.split('AND')]
            range_obj = Range(field=name,lower=lower, upper=upper)
            return range_obj
        elif operator in ['<', '<=']:
            if isinstance(value, str):
                value = re.sub(r'[\'"]', '', value)
            range_obj = Range(field=name, upper=value)
            return range_obj
        elif operator in ['>', '>=']:
            if isinstance(value, str):
                value = re.sub(r'[\'"]', '', value)
            range_obj = Range(field=name, lower=value)
            return range_obj
        elif operator in ['<>', '!=', '=', 'LIKE']:
            negate = operator in ['<>', '!=']
            if isinstance(value, str):
                value = re.sub(r'[\'"]', '', value)
            value_obj = Value(name, items=[value], negate=negate)
            return value_obj
        elif operator in ['IN', 'NOT IN']:
            negate = 'NOT' in operator
            values = re.sub(r'[()]', '', value)
            # Greedy assumption: commas always seperate items
            # Could be a case where a comma is in a string literal, would need different way to split
            values = re.sub(r'[\'"]', '', values)
            values = [v.strip() for v in values.split(',')]
            value_obj = Value(name, items=values, negate=negate)
            return value_obj
        else:
            raise ValueError(f'Unable to handle operator: {operator}')

    @staticmethod
    def convert_json_to_agent(json_data: List[Dict[str, Any]]) -> List[Agent]:
        agents = []
        update_type = Agent.get_kwarg_types()
        for json_agent in json_data:
                # # Set up keyword args to look for expected names and convert them to object names
                # constructor_kwargs = {
                #     'name': json_agent.get('name'),
                #     'current_performance': json_agent.get('current_volume'),
                #     'previous_performance': json_agent.get('historical_average'),
                #     'recent_faceamount': json_agent.get('famt'),
                #     'last_policy_date': json_agent.get('isdt'),
                # }
                # Filter out entries that have None values
                constructor_kwargs = json_agent

                # Convert types as needed
                
                for key, value in constructor_kwargs.items():
                    new_type = update_type.get(key)
                    if key == 'agent':
                        continue
                    
                    if new_type is None and key != 'agent':
                        # logger.warning(f'Update type for key {key} was None. Check configuration of names.')
                        continue
                    try:
                        if not isinstance(value, str):
                            # Do nothing if not string
                            continue
                        elif new_type is datetime:
                            constructor_kwargs[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                        elif new_type is int:
                            constructor_kwargs[key] = int(value)
                        elif new_type is float: 
                            constructor_kwargs[key] = float(value)
                        elif new_type is not str:
                            logger.warning(f'Unable to update for type {new_type}, reconfigure function.')
                            continue
                    except ValueError as e:
                        logger.warning(f'Unable to convert {value} to {new_type}. Error: {str(e)}')

                agent = Agent(**constructor_kwargs)
                agents.append(agent)

        return agents


    @staticmethod
    def post_request(endpoint, data):
        response = requests.post(endpoint, json.dumps(data))
        if response.status_code != 200:
            logger.warning(f'Issue hitting analysis endpoint. Code: {response.status_code}. Content: {response.content}')
            return {}
        else:
            return response.json()


    @staticmethod
    def __read_csv_response(csv_response):
        pass

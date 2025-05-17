
import logging
import os
import re

from typing import Literal, Optional

from application.models import ChatStage
from application.models import Query, QueryType, PerformanceVolumeType, PerformanceQuery, NotWrittenQuery, AgentAmountQuery, OOSQuery, ExplainQuery, Period
from application.models import SQLQuery
from application.querier import prompts 

BASE_PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompts')

logger = logging.getLogger(__name__)

def process_user_intent(input_text: str):
    intent = prompts.get_user_intent(input_text)
    if intent == 'C':
        return ChatStage.EXPLAIN
    else:
        return ChatStage.QUERY

def convert(input_text: str, method: Literal['both', 'selector', 'sql'] = 'both') -> Query:
    if method not in ['both', 'selector', 'sql']:
        return ValueError(f'Unrecognized method: "{method}"')
    # Modifying to handle which way to determine what path
    if method == 'selector':
        intent = prompts.get_user_intent(input_text)
        query_type = convert_to_query_type(intent)
        query = get_query_object(input_text, query_type)
    elif method == 'sql':
        sql_query_text = prompts.get_sql_query(input_text)
        logger.debug(f'SQL Query: {sql_query_text}')
        query_type = review_sql_query(sql_query_text)
        query = get_query_object(input_text, query_type, sql_query_text=sql_query_text)
    elif method == 'both':
        # Selector path
        intent = prompts.get_user_intent(input_text)
        intent_query_type = convert_to_query_type(intent)
        # SQL path
        sql_query_text = prompts.get_sql_query(input_text)
        logger.debug(f'SQL Query: {sql_query_text}')
        sql_query_type = review_sql_query(sql_query_text)

        # NOTE: Pick which one to prefer here
        query_type = intent_query_type
        # Notify if difference.
        if intent_query_type != sql_query_type:
            logger.warning(f'Select found type {intent_query_type} and SQL found type {sql_query_type}. Preferring {query_type}, continuing.')

        query = get_query_object(input_text, query_type, sql_query_text=sql_query_text)

    return query

def review_sql_query(sql_query_text: str) -> QueryType:
    """Logic used to map text from SQL Query prompt to QueryType.

    This function should be in charge of criteria to map to SQL, Performance, OOS, or an other QueryTypes.

    Args:
        sql_query_text (str): response from SQL Query prompt

    Returns:
        QueryType: Query type from user intention
    """
    try:
        SQLQuery.process(sql_query_text)
        if re.search(r'HAVING.*?\(SELECT', sql_query_text, re.DOTALL) is not None:
            return QueryType.PERFORMANCE
        else:
            return QueryType.SQL
    except:
        logger.warning('SQL Query could not be parsed, assuming not valid query')
        return QueryType.OOS


def get_query_object(input_text: str, query_type: QueryType, sql_query_text: str = None) -> Query:
    # TODO: refactor for better understanding of logic flow.
    #     Currently modifying quicky to build new SQLQuery object
    if query_type == QueryType.PERFORMANCE:
        query = create_performance_query(input_text)
        return query
    elif query_type == QueryType.EXPLAIN:
        return ExplainQuery()
    elif query_type == QueryType.OOS:
        return OOSQuery()
    else:
        if sql_query_text is None:
            # If not passed to function, get SQL
            sql_query_text = prompts.get_sql_query(input_text)

        if sql_query_text is None:
            # Not able to get query
            return OOSQuery()
        
        query = SQLQuery(sql_query_text)
        return query
    


def create_performance_query(input_text: str) -> Query:
    performance_type, metric, date_range, frequency = prompts.get_performance_params(input_text)
    if performance_type is None:
        return Query(QueryType.OOS)

    try:
        period = Period(start=date_range[0], end=date_range[1], frequency=frequency)
        volume_type = PerformanceVolumeType(performance_type)
        query = PerformanceQuery(volume_type, metric, period)
        return query
    except ValueError: 
        logger.warning('Unable to convert {volume_type} to PerformanceVolumeType. Either response was bad or Enum needs to be updated for prompt.')
        return OOSQuery()


def create_not_written_query(input_text) -> Query:
    is_not_writen, date_range_param, date_value_param, written_policy = prompts.get_not_written_params(input_text)
    if is_not_writen:
        # True
        query = NotWrittenQuery(date=date_value_param, range=date_range_param, negation=written_policy)
        return query
    else:
        return OOSQuery()


def create_agent_amount_query(input_text) -> Query: 
    is_agent_amount, date_range_param, date_value_param, amount_range_param, amount_value_param, written = prompts.get_agent_amount_params(input_text)
    if is_agent_amount:
        query = AgentAmountQuery(amount_range=amount_range_param, amount_value=amount_value_param, date_value=date_value_param, date_range=date_range_param, negation=not written)
        return query
    else:
        return OOSQuery()

def convert_to_query_type(model_response: Optional[str]) -> QueryType:
    if model_response is None:
        return QueryType.OOS
    try:
        query_type = QueryType(model_response)
        return query_type
    except ValueError:
        logger.warning(f'Unable to convert {model_response} into a QueryType. Either the response was bad or QueryType has not been updated for prompt')
        return QueryType.OOS

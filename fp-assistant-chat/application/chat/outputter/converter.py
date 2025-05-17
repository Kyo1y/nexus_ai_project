
import logging

from datetime import datetime
from typing import List, Union, Tuple

from application.chat.outputter import build
from application.models import Chat
from application.models import Query
from application.models import Response, QueryType, PerformanceVolumeType
from application.models import SQLQuery

# NOTE: Could define function in abstract class and then implement different version to generate different text.
#       Meaning, could have one version output HTML versus plain text.

logger = logging.getLogger(__name__)

def process(response: Response) -> str:
    """Generates response to user from `Response` object. 

    Main function of module. Should be controller to route response to different function. Minimize extra logic here.

    Args:
        response (Response): response object with results from query

    Raises:
        ValueError: QueryType is an unexpected value.

    Returns:
        str: output to the user
    """
    query = response.query
    if isinstance(query, Query.oos): 
        return out_of_scope(response), False
    elif isinstance(query, (Query.performance)): 
        return performance(response), True
    elif isinstance(query, SQLQuery):
        return sql_text(response), True
    elif isinstance(query, Query.not_written):
        return not_written(response), True
    elif isinstance(query, Query.agent_amount):
        return agent_amount(response), True
    else:
        raise ValueError(f'Cannot process query: {query}, need to configure in response builder.')

def explain(prev_chat: Chat) -> str:
    
    chat_line = prev_chat.history[-2]
    query_obj = chat_line.response.query
    original_text = query_obj.original_text
    return original_text

def sql_text(response: Response) -> str:
    # TODO: move to seperate file
    # TODO: make more intelligent intro, GPT call?
    intro = f'{len(response.results)} agents fit the criteria.'
    
    reference_table = build.reference_table()
    response_body = __joiner([intro, reference_table])
    return response_body

def not_written(response: Response) -> str:
    range_coverter = {'After': 'since', 'Before': 'before', 'Between': 'between'}
    # Opener
    total = len(response.results)
    date = convert_date(response.query.date)
    
    date_qual = range_coverter[response.query.range]
    if response.query.negation:
        written_txt = 'not written'
    else:
        written_txt = 'written'


    intro = build.not_written_intro(total, written_txt, date, date_qual)
    # Body
    reference_table = build.reference_table()
    response_body = __joiner([intro, reference_table])
    return response_body

def agent_amount(response: Response) -> str:
    range_coverter = {'After': 'since', 'Before': 'before', 'Between': 'between'}
    date_qual = range_coverter[response.query.date_range]
    # Opener
    total = len(response.results)
    date = convert_date(response.query.date_value)
    
    if response.query.amount_range == 'Between':
        amount = ' to '.join([f'${a:,.2f}' for a in response.query.amount_value])
    else:
        amount = f'${response.query.amount_value:,.2f}'

    if response.query.negation:
        written_txt = 'not written'
    else:
        written_txt = 'written'

    intro = build.agent_amount_intro(total, date, date_qual, amount, written_txt)
    # Body
    reference_table = build.reference_table()
    response_body = __joiner([intro, reference_table])
    return response_body

def performance(response: Response) -> str:
    performance_type = response.query.volume
    abnormality_text = map_intro_text(performance_type)
    performance_intro_line = build.performance_intro(abnormality_text)
    # structured_agent_info = write_table(response)
    # assumption_list = gather_assumptions(response)
    # assumption_list_text = build.assumptions(assumption_list)
    reference_table = build.reference_table()
    response_body = __joiner([performance_intro_line, reference_table])
    return response_body


def gather_assumptions(response: Response):
    assumption_list = []
    assumptions = response.query.assumptions
    period_assumption = build.period_assumption(assumptions.period)
    if period_assumption:
        assumption_list.append(period_assumption)
    return assumption_list

def write_table(response: Response):
    agents = []
    for agent in response.results:
        agent_info_table = build.agent_info(agent.name, agent.previous_performance, agent.current_performance)
        agents.append(agent_info_table)
    return __joiner(agents)

def map_intro_text(performance_type: PerformanceVolumeType):
    if not isinstance(performance_type, PerformanceVolumeType):
        logger.warning(f'Performance type passed was not expected type. {performance_type}. Improper logic will follow.')
    if performance_type == PerformanceVolumeType.LOW:
        return 'abnormally low'
    elif performance_type == PerformanceVolumeType.HIGH:
        return 'abnormally high'
    else:
        return 'abnormal'

def convert_date(date_val: Union[datetime, Tuple[datetime, datetime]], ) -> str:
    if isinstance(date_val, (tuple, list)):
        return ' to '.join([datetime.strftime(d, "%Y-%m-%d") for d in date_val])
    else:
        return datetime.strftime(date_val, "%Y-%m-%d")

def out_of_scope(response: Response) -> str:
    oos_language = build.out_of_scope()
    return oos_language

def __joiner(sections: List[str]):
    return '\n\n'.join(sections)

import os

from typing import List, Optional

from application.models import File
from application.models.requests import Response
from application.models.query import Period
from application.models import QueryType

current_directory = os.path.dirname(__file__)
template_directory = os.path.join(current_directory, 'templates')

class FileManager:
    AGENT_INFO = File(path=os.path.join(template_directory, 'agent_info.txt'))
    PERFORMANCE_INTRO = File(path=os.path.join(template_directory, 'performance_intro.txt'))
    NOT_WRITTE_INTRO = File(path=os.path.join(template_directory, 'not_written_intro.txt'))
    AGENT_AMOUNT_INTRO = File(path=os.path.join(template_directory, 'agent_amount_intro.txt'))
    OPENER = File(path=os.path.join(template_directory, 'opener.txt'))
    CLOSER = File(path=os.path.join(template_directory, 'closer.txt'))
    SUMMARY = File(path=os.path.join(template_directory, 'summary_line.txt'))
    EXPLAIN_LINE = File(path=os.path.join(template_directory, 'explain_line.txt'))
    ASSUMPTIONS = File(path=os.path.join(template_directory, 'assumptions.txt'))
    ERROR = File(path=os.path.join(template_directory, 'error.txt'))
    OOS = File(path=os.path.join(template_directory, 'oos.txt'))
    PERIOD_ASSUMPTION = File(path=os.path.join(template_directory, 'period.txt'))
    SEE_TABLE = File(path=os.path.join(template_directory, 'reference_table.txt'))


def opening_text() -> str:
    return FileManager.OPENER.text

def closing_text() -> str:
    return FileManager.CLOSER.text

def summary_line(agent_list: List[str], evaluation: str) -> str:
    """builds summary line to describe information

    Args:
        agent_list (): list of found agents
        evaluation (str): crieteria that was used to search for

    Returns:
        str: first line giving summary of results
    """
    if len(agent_list) == 1:
        agent_name = agent_list[0]
        opener_stub = f'Only agent {agent_name} has'
    elif len(agent_list) == 2:
        agent_names = ' and '.join(agent_list)
        opener_stub = f'Agents {agent_names} have'
    else:
        first_agent_names = ', '.join(agent_list[:-1])
        agent_names = f'{first_agent_names}, and {agent_list[-1]}'
        opener_stub = f'Agents {agent_names} have'
    text = FileManager.SUMMARY.substitute(opener_stub=opener_stub, evaluation=evaluation)
    return text

def explain_line(agent_name: str, relation: str, amount: str) -> str:
    if relation not in ['over', 'under']:
        raise ValueError(f'Parameter relation must be either "over" or "under", not "{relation}".')
    text = FileManager.EXPLAIN_LINE.substitute(name=agent_name, relation=relation, amount=amount)
    return text

def assumptions(assumption_list: List[str]):
    assumption_list = convert_list(assumption_list)
    text = FileManager.ASSUMPTIONS.substitute(assumption_list=assumption_list)
    return text

def error():
    return FileManager.ERROR.text

def out_of_scope():
    return FileManager.OOS.text

def convert_list(list_items: List[str], line_fmt: str = '-  {}') -> str:
    """Returns a formatted string of a list of strings. Joins list items on individual lines

    Args:
        list_items (List[str]): List to format
        line_fmt (str, optional): format string to use. Defaults to '-  {}'.

    Returns:
        str: formatted string of the list
    """
    return '\n'.join([line_fmt.format(fact) for fact in list_items])

def agent_info(agent_name:str, hist_perf:str, curr_perf:str) -> str:
    return FileManager.AGENT_INFO.substitute(agent_name=agent_name, historical_norm=hist_perf, current_business_volume=curr_perf)
    
def performance_intro(abnormality_text):
    return FileManager.PERFORMANCE_INTRO.substitute(abnormality=abnormality_text)

def not_written_intro(total, written, date, date_qual):
    return FileManager.NOT_WRITTE_INTRO.substitute(total=total, written=written, date=date, date_qualifier=date_qual)

def agent_amount_intro(total, date, date_qual, amount, written):
    return FileManager.AGENT_AMOUNT_INTRO.substitute(total=total, date=date, amount=amount, written=written, date_qualifier=date_qual)

def period_assumption(period: Optional[Period]):
    if period is None:
        return None
    interval_date_string = str(period)
    frequency = period.frequency
    return FileManager.PERIOD_ASSUMPTION.substitute(period=interval_date_string, frequency=frequency)

def reference_table():
    return FileManager.SEE_TABLE.text

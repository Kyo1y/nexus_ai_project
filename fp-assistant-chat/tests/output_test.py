from datetime import datetime

from application.chat.outputter import build
from application.chat.outputter import converter
from application.models import Response, NotWrittenQuery, PerformanceQuery, AgentAmountQuery, OOSQuery, Agent

def process_query(query, agents=None) -> str:
    """Helper function to convert query to response text. 

    Just used to reduce repeated code

    Args:
        query (_type_): _description_

    Returns:
        str: user text
    """
    response = Response(query, results=agents)
    response_txt = converter.process(response)[0]
    return response_txt

class TestProcess:
    def test_out_of_scope(self):
        query = OOSQuery()
        response_txt = process_query(query)
        expected_txt = build.out_of_scope()
        assert response_txt == expected_txt
    
    def test_not_written_after(self):
        num_agents = 10
        date = datetime(2022, 2, 13)
        
        query = NotWrittenQuery(date=date, range='After')
        date_str = converter.convert_date(date)
        agents = [Agent('name') for i in range(num_agents)]
        
        # Run Process
        response_txt = process_query(query, agents)

        # Check for output
        expected_intro = build.not_written_intro(num_agents, False, date_str, 'since')
        reference_table = build.reference_table()
        expected_txt = f'{expected_intro}\n\n{reference_table}'
        return response_txt == expected_txt
    
    def test_not_written_between(self):
        num_agents = 13
        date = [datetime(2022, 2, 13), datetime(2023, 1, 3)]
        
        query = NotWrittenQuery(date=date, range='Between')
        date_str = converter.convert_date(date)
        agents = [Agent('name') for i in range(num_agents)]
        
        # Run Process
        response_txt = process_query(query, agents)

        # Check for output
        expected_intro = build.not_written_intro(num_agents, False, date_str, 'between')
        reference_table = build.reference_table()
        expected_txt = f'{expected_intro}\n\n{reference_table}'
        return response_txt == expected_txt
    
    def test_not_written_before(self):
        num_agents = 8
        date = datetime(2023, 1, 3)
        
        query = NotWrittenQuery(date=date, range='Before')
        date_str = converter.convert_date(date)
        agents = [Agent('name') for i in range(num_agents)]
        
        # Run Process
        response_txt = process_query(query, agents)

        # Check for output
        expected_intro = build.not_written_intro(num_agents, False, date_str, 'before')
        reference_table = build.reference_table()
        expected_txt = f'{expected_intro}\n\n{reference_table}'
        return response_txt == expected_txt


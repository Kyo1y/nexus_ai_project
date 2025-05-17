import logging
import os
import re

from datetime import datetime
from typing import Optional, Tuple

from application import openai_manager
from application.openai_manager.requests import process_single_request
from application.models import File
from application.models import PromptTree, PromptNode
from application.querier.prompts import extract
from application.utils.datetime import datetime_to_str

BASE_PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompt_files')

logger = logging.getLogger(__name__)

def get_prompt(file_path, input_text, **kwargs):
    filepath = os.path.join(BASE_PROMPT_PATH, file_path)
    file = File(path=filepath, is_template=True)
    prompt_text = file.substitute(input_text = input_text, **kwargs)
    return prompt_text

def get_prompt_tree(input_text: str):
    # NOTE: Not currently used, need to update prompt tree to be able to properly select path to take
    selector = PromptNode('selector', get_prompt('query_selector.txt', input_text), endpoint='chat.completions')
    
    # Question 0: Over/Under performing
    abnormal_performance = PromptNode('abnormal_performance', get_prompt('abnormal_agent_performance.txt', input_text), endpoint='chat.completions')

    # Question 1: Inactive Agents
    is_inactive_agents = PromptNode('is_inactive_agents', get_prompt('inactive_agents/is_inactive_agents.txt', input_text), endpoint='chat.completions')
    agent_inactivity_date = PromptNode('agent_inactivity_date', get_prompt('inactive_agents/agent_inactivity_date.txt', input_text), endpoint='chat.completions')
    agent_inactivity_written_policy = PromptNode('agent_inactivity_written_policy', get_prompt('inactive_agents/written_policy.txt', input_text), endpoint='chat.completions')

    # Question 2: Agents over face amount
    is_policy_face_amount = PromptNode('is_policy_face_amount', get_prompt('policies_face_amount/is_policy_face_amount.txt', input_text), endpoint='chat.completions')
    policy_date = PromptNode('policy_date', get_prompt('policies_face_amount/policy_date.txt', input_text), endpoint='chat.completions')
    policy_face_amount = PromptNode('policy_face_amount', get_prompt('policies_face_amount/policy_face_amount.txt', input_text), endpoint='chat.completions')
    face_amount_written_policy = PromptNode('face_amount_written_policy', get_prompt('policies_face_amount/written_policy', input_text), endpoint='chat.completions')


def get_user_intent(input_text: str) -> Optional[str]:
    # selector = PromptNode('selector', get_prompt('query_selector.txt', input_text), model='gpt-4', endpoint='chat.completions')
    # selector = openai_manager.process_prompt_nodes([selector])[0]
    # value = extract.selector(selector.response)
    query_selector_prompt = get_prompt('query_selector.txt', input_text)
    message_list = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': query_selector_prompt},
    ]
    initial_response = process_single_request(message_list)
    initial_value = extract.selector(initial_response)
    if initial_value == 'A':
        message_list.append({'role':'assistant', 'content':initial_response})
        follow_up_prompt = get_prompt('follow_up.txt', '')
        message_list.append({'role':'user', 'content':follow_up_prompt})
        follow_up_response = process_single_request(message_list)
        value = extract.selector(follow_up_response)
        return value
    else:
        return initial_value

def get_sql_query(input_text: str) -> Optional[str]:
    now = datetime.now().strftime('%Y-%m-%d')
    sql_converter = PromptNode('sql_converter', get_prompt('sql_converter.txt', input_text, current_date=now), model='gpt-4', endpoint='chat.completions')
    sql_converter = openai_manager.process_prompt_nodes([sql_converter])[0]
    return sql_converter.response

def get_performance_params(input_text: str) -> Tuple[str]:
    # Set up prompt nodes
    abnormal_performance = PromptNode('abnormal_performance', get_prompt('abnormal_agent_performance.txt', input_text), model='gpt-4', endpoint='chat.completions')
    now = datetime.now().strftime('%Y-%m-%d')
    policy_date = PromptNode('policy_date', get_prompt('policy_date_2.txt', input_text, current_date=now), model='gpt-4', endpoint='chat.completions')
    frequency = PromptNode('frequency', get_prompt('performance_freq.txt', input_text, current_date=now), model='gpt-4', endpoint='chat.completions')
    metric = PromptNode('metric', get_prompt('performance_metric.txt', input_text), model='gpt-4', endpoint='chat.completions')
    abnormal_performance, metric, policy_date, frequency = openai_manager.process_prompt_nodes([abnormal_performance, metric, policy_date, frequency])
    # Get exact response from GPT
    performance_param = extract.performance(abnormal_performance.response)
    metric_param = extract.metric(metric.response)
    date_param = extract.date(policy_date.response)
    frequency_param = extract.frequency(frequency.response)
    return performance_param, metric_param, date_param, frequency_param


def get_not_written_params(input_text: str) -> Tuple[Optional[bool], Optional[datetime]]:
    is_inactive_agents = PromptNode('is_inactive_agents', get_prompt('is_inactive_agents.txt', input_text), model='gpt-4', endpoint='chat.completions')
    now = datetime.now().strftime('%Y-%m-%d')
    agent_inactivity_date = PromptNode('agent_inactivity_date', get_prompt('agent_inactivity_date.txt', input_text=input_text, current_date=now), model='gpt-4', endpoint='chat.completions')
    agent_inactivity_written_policy = PromptNode('agent_inactivity_written_policy', get_prompt('written_policy.txt', input_text=input_text), model='gpt-4', endpoint='chat.completions')

    is_inactive_agents, agent_inactivity_date, agent_inactivity_written_policy = openai_manager.process_prompt_nodes([is_inactive_agents, agent_inactivity_date, agent_inactivity_written_policy])

    is_inactive_param = extract.yes_or_no(is_inactive_agents.response, 'Intent')
    logger.debug(f'Indicator Response: {is_inactive_param}. Note: not currently being used - always returns true from function call.')
    written_policy_param = extract.yes_or_no(agent_inactivity_written_policy.response, 'Written')
    date_range_param = extract.date_range(agent_inactivity_date.response)
    date_value_param = extract.date_value(agent_inactivity_date.response, date_range_param)

    return True, date_range_param, date_value_param, written_policy_param

def get_agent_amount_params(input_text: str) -> Tuple[Optional[bool], Optional[datetime], Optional[int]]:
    is_policy_face_amount = PromptNode('is_policy_face_amount', get_prompt('policies_face_amount/is_policy_face_amount.txt', input_text), model='gpt-4', endpoint='chat.completions')
    now = datetime.now().strftime('%Y-%m-%d')
    policy_date = PromptNode('policy_date', get_prompt('policies_face_amount/policy_date_2.txt', input_text, current_date=now), model='gpt-4', endpoint='chat.completions')
    policy_face_amount = PromptNode('policy_face_amount', get_prompt('policies_face_amount/policy_face_amount.txt', input_text=input_text), model='gpt-4', endpoint='chat.completions')
    face_amount_written_policy = PromptNode('face_amount_written_policy', get_prompt('policies_face_amount/written_policy.txt', input_text=input_text), model='gpt-4', endpoint='chat.completions')

    is_policy_face_amount, policy_date, policy_face_amount, face_amount_written_policy = openai_manager.process_prompt_nodes([is_policy_face_amount, policy_date, policy_face_amount, face_amount_written_policy])
    is_policy_param = extract.yes_or_no(is_policy_face_amount.response, 'Intent')
    logger.debug(f'Indicator Response: {is_policy_param}. Note: not currently being used - always returns true from function call.')
    written_policy_param = extract.yes_or_no(face_amount_written_policy.response, 'Written')
    # date_range_param = extract.date_range(policy_date.response)
    # date_value_param = extract.date_value(policy_date.response, date_range_param)
    date_range_param, date_value_param = extract.extract_date_q3(policy_date.response)
    face_amount_range_param = extract.amount_range(policy_face_amount.response)
    face_amount_param = extract.amount_value(policy_face_amount.response, face_amount_range_param)

    return True, date_range_param, date_value_param, face_amount_range_param, face_amount_param, written_policy_param


if __name__ == '__main__':
    # test_input = "Which agents in my office have abnormally high performance?"
    test_input = "Yo, can you show me all agents in office B56 who haven't written a policy in the last 8 months?"

    resp = get_user_intent(test_input)
    print(resp)
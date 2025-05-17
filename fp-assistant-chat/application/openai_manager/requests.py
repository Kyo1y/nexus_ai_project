from __future__ import annotations

import logging

import openai


from dataclasses import dataclass
from typing import List, TYPE_CHECKING

from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log
if TYPE_CHECKING:
    from application.models import PromptNode
from application.openai_manager import constants
from application.openai_manager import defaults
from application.openai_manager import payload
from application.openai_manager.multi_client import OpenAIMultiClient



@dataclass
class RequestDefaults:
    """Data class used to easily pass constant values to requests"""
    temperature: float = 0.0
    max_tokens: int  = 265
    frequency_penalty: int = 0
    presence_penalty: int = 0

    def __iter__(self):
        return iter(self.__dict__.items())

RETRY_ATTEMPTS = 5
WAIT_LENGTH = 2

logger = logging.getLogger(__name__)

def asynchronous_requests(prompt_list: list):
    # TODO: Can we add more calls to queue after it has started?

    # Loads in data template that is passed in to every request by default
    client = OpenAIMultiClient(endpoint="chat.completions", data_template=dict(RequestDefaults()))
    # Pass request function in and make calls
    client.run_request_function(make_requests, client, prompt_list)
    # Wait until all responses have been recieved
    responses = client.pull_all()

    # Client closes auto-magically after run_request_function completes, 
    # don't need to worry about calling manually.

    # Process responses
    prompt_list = __process_responses(responses, prompt_list)
    return prompt_list

def synchronous_request(prompt, model=None, endpoint=None, full_response=False):
    if not endpoint:
        endpoint = constants.ENDPOINT.COMPLETION

    if not model:
        if endpoint == constants.ENDPOINT.COMPLETION:
            model = defaults.MODEL.COMPLETION
        elif endpoint == constants.ENDPOINT.CHAT:
            model = defaults.MODEL.CHAT
    
    response = __call_endpoint(model, prompt, endpoint, full_response)
    return response

@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(WAIT_LENGTH), before_sleep=before_sleep_log(logger, logging.DEBUG))
def __call_endpoint(model, prompt, endpoint, full_response: bool):
    logger.debug(f'Synchronus call to endpoint "{endpoint}" with model "{model}"')
    if endpoint == constants.ENDPOINT.COMPLETION:
        # Process responses for completions endpoint
        logger.warning(f'Calling completion with model {model}')
        response = openai.Completion.create(model=model,
                                            prompt=prompt,
                                            **dict(RequestDefaults()),
                                            )
        if full_response:
            return response
        return response['choices'][0]['text']
    elif endpoint == constants.ENDPOINT.CHAT:
        # Process response for chat.completions endpoint
        messages = prompt
        if isinstance(messages, str):
            # Convert to string message to expected list format
            messages = __convert_str_to_messages(messages) 
        response = openai.ChatCompletion.create(model=model,
                                                messages=messages,
                                                **dict(RequestDefaults())
                                                )
        if full_response:
            return response
        return response['choices'][0]['message']['content']
    else:
        logger.warning(f'Unrecognized endpoint {endpoint}')
        return None
    
def process_single_request(message_list, model='gpt-4'):
    return openai.ChatCompletion.create(model=model, messages=message_list, temperature=0)['choices'][0]['message']['content']


def process_prompt_nodes(prompt_nodes: List[PromptNode]) -> List[PromptNode]:
    # Step 1: Prep
    client = OpenAIMultiClient(endpoint="chat.completions", data_template=dict(RequestDefaults()))
    # Request
    
    # Step 2: Pass request function in and make calls
    client.run_request_function(request_prompt_node, client, prompt_nodes)
    # Wait until all responses have been recieved
    responses = client.pull_all()
    
    # Step 3: Update
    for response in responses:
        prompt_index = int(response['metadata']['prompt_index'])
        prompt_node = prompt_nodes[prompt_index]
        prompt_node.failed = response['failed']

        # Copy output to response value
        if response['failed']:
            prompt_node.response = 'Unspecified'
            logger.error(f'Retry failed for extraction for request with metadata {response["metadata"]}.')
        elif response['endpoint'] == constants.ENDPOINT.COMPLETION:
            # Process responses for completions endpoint
            prompt_node.response = response['response']['choices'][0]['text']
        elif response['endpoint'] == constants.ENDPOINT.CHAT:
            # Process response for chat.completions endpoint
            prompt_node.response = response['response']['choices'][0]['message']['content']
        else:
            logger.warning(f'Unrecognized endpoint {response["endpoint"]} for request with metadata {response["metadata"]}')

    return prompt_nodes

def request_prompt_node(client: OpenAIMultiClient, prompt_nodes: List[PromptNode]):
    for p_index, prompt_node in enumerate(prompt_nodes):
        data = payload.build_data(prompt_node.base_prompt, prompt_node.model, prompt_node.endpoint)
        metadata = {'prompt_index': p_index, 'prompt_node': prompt_node, 'prompt_name': prompt_node.name}
        endpoint = prompt_node.endpoint
        client.request(data=data, endpoint=endpoint, metadata=metadata)


def convert_prompt_node(prompt_node: PromptNode):
    payload_data = payload.build_data(prompt_node.base_prompt, prompt_node.model, prompt_node.endpoint)
    pre_payload = {
        'data': payload_data,
        'metadata': {'prompt_node': prompt_node, 'prompt_name': prompt_node.name},
        'endpoint': prompt_node.endpoint
        }
    return payload_data

def make_requests(client: OpenAIMultiClient, prompt_list: list):
    for p_index, prompt_dict in enumerate(prompt_list):
        # Assumes each prompt_list has the following keys
        # Metadata is used to attach data to the async call, not used in call itself
        data_dict = prompt_dict['data']
        # Add in prompt_index to meatdata so info can be updated after call
        metadata_dict = {'prompt_index': p_index, **prompt_dict.get('metadata', {})}
        if 'prompt_name' not in metadata_dict:
            metadata_dict['prompt_name'] = f'Prompt #{p_index}'
        prompt_endpoint = prompt_dict['endpoint']
        client.request(data=data_dict, metadata=metadata_dict, endpoint=prompt_endpoint)


def __convert_str_to_messages(prompt_str: str):
    """Creates message list to use for ChatGPT calls

    Args:
        prompt_str (str): prompt text to be turned into message list

    Returns:
        list: list of dictionaries containing message information
    """
    message_list = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': f'{prompt_str}'},
    ]
    return message_list

def __process_responses(model_responses:list, prompt_queue:list):
    """Processes model responses and updates the prompt queue.

    Args:
        model_responses (list): List of model responses.
        prompt_queue (list): List of dictionaries representing prompt information.

    Returns:
        list: Updated prompt queue with processed model responses.
    """
    for response in model_responses:
        prompt_index = int(response['metadata']['prompt_index'])

        if response['failed']:
            prompt_queue[prompt_index].update({
                'completion': 'Unspecified',
                'failed': response['failed']
            })
            logger.error(f'Retry failed for extraction for request with metadata {response["metadata"]}.')
        else:
            if response['endpoint'] == constants.ENDPOINT.COMPLETION:
                # Process responses for completions endpoint
                prompt_queue[prompt_index].update({
                    'completion': response['response']['choices'][0]['text'],
                    'failed': response['failed']
                })
            elif response['endpoint'] == constants.ENDPOINT.CHAT:
                # Process response for chat.completions endpoint
                prompt_queue[prompt_index].update({
                    'completion': response['response']['choices'][0]['message']['content'],
                    'failed': response['failed']
                })
            else:
                logger.warning(f'Unrecognized endpoint {response["endpoint"]} for request with metadata {response["metadata"]}')
    return prompt_queue

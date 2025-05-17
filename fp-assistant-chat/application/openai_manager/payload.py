import logging

from dataclasses import dataclass
from typing import Any, Optional

from application.openai_manager import constants
from application.openai_manager import defaults

logger = logging.getLogger(__name__)

@dataclass
class Payload:
    endpoint: str
    data: dict
    metadata: Optional[dict]
    max_retries: int
    retry_multiplier: float
    retry_max: float
    attempt: int = 0
    failed: bool = False
    response: Any = None
    callback: Any = None

    def call_callback(self):
        if self.callback:
            self.callback(self)


def build_data(prompt, model=None, endpoint=None, str_to_msg_func=None):
    # TODO: This should live somewhere else. Unsure of where now though

    if not endpoint:
        endpoint = constants.ENDPOINT.COMPLETION
    
    if not model:
        if endpoint == constants.ENDPOINT.CHAT:
            model = defaults.MODEL.CHAT
        elif endpoint == constants.ENDPOINT.COMPLETION:
            model = defaults.MODEL.COMPLETION
    
    if endpoint == constants.ENDPOINT.COMPLETION:
        logger.warning(f'Calling completion with model {model}')
        return {'prompt': prompt, 'model': model}
    elif endpoint == constants.ENDPOINT.CHAT:
        if str_to_msg_func:
            messages = str_to_msg_func(prompt)
        else:
            messages = __convert_str_to_messages(prompt)
        return {'messages': messages, 'model': model}
    else:
        logger.warning(f'Endpoint {endpoint} not recognized, will cause issues downstream. Fix input var for prompt node.')
    return {}



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
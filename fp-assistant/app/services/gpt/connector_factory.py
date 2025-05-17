from .connector import CompletionConnector, ChatCompletionConnector

import logging

logger = logging.getLogger("logger")

completion_model_list = [
    'text-davinci-003'
]

chat_completion_model_list = [
    'gpt-3.5-turbo',
    'gpt-4',
    'gpt-4-1106-preview'
]

def get_connector(connector_data):
    if connector_data['gpt']['model'] in completion_model_list:
        return CompletionConnector(connector_data)
    elif connector_data['gpt']['model'] in chat_completion_model_list:
        return ChatCompletionConnector(connector_data)
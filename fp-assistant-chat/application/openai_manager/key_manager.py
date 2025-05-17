"""Class that manages the api key for OpenAI. 
"""
import json
import os
import logging

import openai

from application.utils.os import load_file
from application.configs import config

RECOGNIZED_MODES = ['manual', 'roundrobin', 'maxout']
STATE_PATH = os.path.join(os.path.dirname(__file__), 'state', 'state.json')

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self, key_list, mode='manual', current_key=None) -> None:
        self.keys = key_list
        self.key_index = 0

        self._mode = mode
        openai.api_key = current_key

        if os.path.isfile(STATE_PATH):
            state = load_file(STATE_PATH)
            self.current_key = state['api_key']
            self.mode = state['mode']
        else:
            os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
            self.save()

    def call_made(self):
        if self.mode == 'roundrobin':
            # Mode: Switch key after every call
            # Ensure that key is within range of keys
            new_index = (self.key_index + 1) % len(self.keys)
            new_key = self.keys[new_index]
            self.current_key = new_key
            self.key_index = new_index

    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, value):
        if value not in RECOGNIZED_MODES:
            logger.warning(f'Mode {value} not in recognized list. Behavior of key management may not be desirable.')
        self._mode = value
        self.save()

    @property
    def current_key(self):
        return openai.api_key

    @current_key.setter
    def current_key(self, value):
        self._current_key = value
        openai.api_key = value
        logger.debug(f'Updated key, last four is {value[-4:]}')
        self.save()

    def save(self):
        try:
            with open(STATE_PATH, 'w') as json_file:
                
                json.dump({'api_key': self.current_key, 'mode': self.mode}, json_file)
        except Exception as e:
            logger.exception('Unable to save API key manager state.')

key_manager = KeyManager(config.API_KEY_LIST, config.API_KEY_MODE, config.API_KEY)

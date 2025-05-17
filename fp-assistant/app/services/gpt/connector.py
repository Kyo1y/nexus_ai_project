from abc import ABC, abstractclassmethod
from app.config import get_settings

import logging
import openai
import time

logger = logging.getLogger("logger")


class Connector(ABC):

    openai.api_key = get_settings().gpt_key
    openai.api_requestor.TIMEOUT_SECS = get_settings().gpt_timeout
    
    @abstractclassmethod
    def get_gpt_response(self, input) -> None:
        pass

    def get_response(self, input):
        gpt_call_count = 0

        while gpt_call_count < get_settings().gpt_call_limit:
            try:
                response = self.get_gpt_response(input)
                return response
            except openai.error.Timeout as e:
                logger.warning("gpt timeout error => gpt call count: " + str(gpt_call_count + 1))
                gpt_call_count += 1
            except openai.error.RateLimitError as e:
                logger.warning("gpt rate limit error => gpt call count: " + str(gpt_call_count + 1))
                gpt_call_count += 1
                if gpt_call_count < get_settings().gpt_call_limit: time.sleep(60)
        else:
            logger.error("gpt call limit reached => terminating gpt call")
            return ""


class CompletionConnector(Connector):

    def __init__(self, connector_data):
        self.connector_data = connector_data
        self.model = connector_data['gpt']['model']
        self.temperature = connector_data['gpt']['temperature']
        self.max_tokens = connector_data['gpt']['max_tokens']
        self.prompt = connector_data['prompt']

    def get_gpt_response(self, input):
        logger.info("*****" + self.connector_data['name'] + " ==> MAKING GPT CALL*****")

        response = openai.Completion.create(
            engine = self.model,
            prompt = self.prompt + "\n" + input['data'] + "\n\nCOMPLETION\n",
            temperature = self.temperature,
            top_p = 1,
            max_tokens = self.max_tokens,
            frequency_penalty = 0,
            presence_penalty = 0
        )
        return response.choices[0].text    


class ChatCompletionConnector(Connector):

    def __init__(self, connector_data):
        self.connector_data = connector_data
        self.model = connector_data['gpt']['model']
        self.temperature = connector_data['gpt']['temperature']
        self.max_tokens = connector_data['gpt']['max_tokens']
        self.messages = connector_data['messages']

    def get_gpt_response(self, input):
        logger.info("*****" + self.connector_data['name'] + " ==> MAKING GPT CALL*****")

        self.messages.append({"role": "user", "content": input['data']})

        request_body = { 
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "top_p": 1,
            "max_tokens": self.max_tokens,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        response = openai.ChatCompletion.create(**request_body)

        return response['choices'][0]['message']['content']


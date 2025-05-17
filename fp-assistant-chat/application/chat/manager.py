import datetime
import logging

import pandas as pd

from typing import Any, Dict, List, Optional, Tuple

from application import querier
from application import requestor
from application.chat import outputter
from application.models import Chat, ChatStage
from application.models import Response
from application.models import Query
from application.sessions import session_manager


logger = logging.getLogger(__name__)

AGENT_NAME = 'agent'
USER_NAME = 'user'

def create_chat(user_id: Optional[str]):
    # Create user if they don't exist
    chat_obj = session_manager.create_chat_session(user_id)

    opening_text = outputter.build.opening_text()
    chat_obj.record_chat(sender=AGENT_NAME, message=opening_text)
    logger.info(f'New chat started with ID {chat_obj.id} for user {chat_obj.user_id}')
    session_manager.update_session_data(chat_obj.user_id, chat_obj.id, chat_obj)
    return opening_text, chat_obj.id, chat_obj.user_id


def continue_chat(user_id, chat_id, input_text: str, identity=None) -> Tuple[dict, int]:
    """Processes the user input and return response

    Args:
        chat_obj (Chat): chat object containing relevant information
        input_text (str): text from user

    Returns:
        str: response to give back to user
    """
    try:
        chat_obj = session_manager.get_chat_session(chat_id)
    except KeyError:
        logger.exception(f'Chat ID provided ({chat_id}) does not exist.')
        return {'error', 'Chat ID provided in URL does not exist. Ensure you are passing in chat id recieved from calling /chat'}, 404

    chat_text = clean_text(input_text)
    chat_obj.record_chat(sender=USER_NAME, message=chat_text)

    # 3 Steps: process, transition, respond
    
    # TODO: add query/response to chat_object
    response = process_input(chat_obj, chat_text, identity)
    chat_obj.stage = transition_chat(chat_obj)
    response_text, display_table = prepare_user_response(chat_obj, response)

    # Update information
    chat_obj.record_chat(sender=AGENT_NAME, message=response_text, response=response)
    session_manager.update_session_data(user_id, chat_id, chat_obj)

    table_json = None
    if display_table: 
        html_table = outputter.renderer.html_agent_table(response)
        df = outputter.renderer.build_data(response.results, response.dtypes)
        if isinstance(df, pd.DataFrame) and not df.empty:
            data_table = df.to_dict(orient='records')
            # Remove key from being shown
            data_header = [{'id': col, 'label':col} for col in df.columns if col not in ['key', 'Agent']]
        else:
            data_table = None
            data_header = None


        table_json, cols = prepare_table_json(response)
        return {'chat': response_text, 'response_obj': response, 'display_table': display_table, 'responses':table_json, 'data_table': data_table, 'data_header': data_header, 'columns': cols, 'html_table': html_table}, 200
        
    return {'chat': response_text, 'response_obj': response, 'display_table': display_table}, 200

def prepare_table_json(response: Response) -> List[Dict[str, Any]]:

    agent_json = []
    cols = set()
    for agent in response.results: 
        json_repr = agent.json()
        agent_json.append(json_repr)
        cols.update(set(json_repr.keys()))

    return agent_json, cols


def clean_text(input_text: str) -> str:
    clean_text = input_text.strip()
    return clean_text

def process_input(chat_obj: Chat, input_text: str, identity: Optional[str] = None) -> Response:
    # Currently, input is processed the same regardless of where in the chat we are.
    # Query object should be created everytime.
    # Leaving conditional for future when stage matters
    if chat_obj.stage in [ChatStage.CREATION, ChatStage.QUERY]:
        # First chat, do anything different from query?
        pass
    elif chat_obj.stage == ChatStage.EXPLAIN:
        # Submit query
        pass
    else:
        logger.warning(f'Unrecognized chat stage of {chat_obj.stage}, cannot process correctlty')

    query = querier.convert(input_text, method='both')
    query.identity = identity
    response = requestor.get_data(query)
    return response

def transition_chat(chat_obj: Chat) -> ChatStage:
    if ChatStage.CREATION == chat_obj.stage:
        return ChatStage.QUERY
    elif ChatStage.QUERY == chat_obj.stage:
        return ChatStage.QUERY
    else:
        logger.warning(f'Unrecognized chat stage of {chat_obj.stage}, defaulting to "QUERY"')
        return ChatStage.QUERY

def prepare_user_response(chat_obj: Chat, response: Response) -> str:
    # Again, chat stage does not dictate how to output a response currently.
    # Leaving for convience later
    if ChatStage.CREATION == chat_obj.stage:
        pass
    elif ChatStage.QUERY == chat_obj.stage:
        pass
    if isinstance(response.query, Query.explain):
        # Explain
        output_text = outputter.converter.explain(chat_obj)
        display_table = False
    else:
        output_text, display_table = outputter.converter.process(response)
    return output_text, display_table

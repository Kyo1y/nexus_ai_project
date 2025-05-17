import os
import json
import logging

from typing import Optional, Union, Dict

from application import utils
from application.models.chat import Chat, ChatStage, ChatLine
from application.models.user import User


logger = logging.getLogger(__name__)



# get_user
# get_chat

class SessionDAO:
    # Handles logic for loading in data
    # TODO: Make JSON version and Mongo version

    def __init__(self):
        pass

    def user_exists(self, user_id: str) -> bool: pass
    def load_user(self, user_id: str) -> User: pass
    def create_user_id(self) -> str: pass
    def create_user(self, user_id: str) -> User: pass
    def save_user(self, user: User) -> None:
        pass
    def update_user(self, user: User) -> None:
        pass

    def get_user(self, user_id: str) -> User:
        """Gets user from user_id, creates if doesn't exist"""
        # TODO: Does it make sense to create user if doesn't exist?
        # Assumes missing user_id is okay, create new user
        if user_id is None:
            # TODO: Should this be handled elsewhere?
            user_id = self.create_user_id()

        if self.user_exists(user_id):
            user = self.load_user(user_id)
        else:
            user = self.create_user(user_id)
            self.save_user(user)
        return user
    
    
    def chat_exists(self, chat_id: str) -> bool: pass
    def load_chat(self, chat_id: str) -> Chat: pass
    def create_chat(self, chat_id,): pass
    def create_chat_id(self) -> str: pass
    def save_chat(self, chat: Chat) -> None: pass
    def update_chat(self, chat: Chat) -> None: pass
    def remove_chat(self, chat: Chat) -> None: pass

    def get_chat(self, chat_id: str) -> Chat:
        # Gets chat if exists, throws error if it doesn't
        if self.chat_exists(chat_id):
            chat = self.load_chat(chat_id)
        else:
            raise KeyError(f'Chat with ID {chat_id} does not exist.')

        return chat


class SessionDataJSON(SessionDAO):
    """
        users = {user_id (str): user.User}
    """
    def __init__(self, session_path):
        self.user_json_path = os.path.join(session_path, 'users.json')
        self.chat_json_path = os.path.join(session_path, 'chats.json')

        # Make directory if it is missing
        if not os.path.isdir(session_path):
            os.makedirs(session_path, exist_ok=True)
        
        # Create/load user data
        if os.path.isfile(self.user_json_path):
            try:
                with open(self.user_json_path, 'r') as json_file:
                    json_user_data = json.load(json_file)
                    self.user_data = self.convert_dict_to_user(json_user_data)
            except Exception as e:
                logger.exception('Failed to load json file for session manager.')
                self.user_data = {}
        else:
            logger.debug('Created empty session object')
            self.user_data = {}
        
        # Create/load chat data
        if os.path.isfile(self.chat_json_path):
            try:
                with open(self.chat_json_path, 'r') as json_file:
                    json_chat_data = json.load(json_file)
                    self.chat_data = self.convert_dict_to_chat(json_chat_data)
            except Exception as e:
                logger.exception('Failed to load json file for session manager.')
                self.chat_data = {}

        else:
            logger.debug('Created empty session object')
            self.chat_data = {}

    @staticmethod
    def convert_dict_to_chat(json_chat_data: dict) -> Dict[str, Chat]:
        # For every chat, convert dict to Chat object
        chat_data = {}
        for chat_id, chat_dict in json_chat_data.items():
            chat_dict['stage'] = ChatStage[chat_dict['stage']]
            chat_dict['stage_log'] = [ChatStage[stage] for stage in chat_dict.get('stage_log', [])]
            new_history = []
            for history_i in chat_dict['history']:
                if isinstance(history_i, ChatLine):
                    new_history.append(history_i)
                else:
                    new_history.append(ChatLine(**history_i))
            chat_dict['history'] = new_history
            chat_dict['created'] = utils.datetime.str_to_datetime(chat_dict['created'])
            chat_data[chat_id] = Chat(**chat_dict)
        return chat_data


    @staticmethod
    def convert_dict_to_user(json_user_data: dict) -> Dict[str, User]:
        # For every chat, convert dict to Chat object
        user_data = {}
        for user_id, user_dict in json_user_data.items():
            user_dict['created'] = utils.datetime.str_to_datetime(user_dict['created'])
            user_data[user_id] = User(**user_dict)
        return user_data

    def user_exists(self, user_id: str) -> bool:
        return user_id in self.user_data

    def load_user(self, user_id: str) -> User:
        return self.user_data[user_id]

    def create_user(self, user_id: str) -> User:
        return User(user_id)

    def save_user(self, user: User) -> None:
        self.user_data[user.id] = user

    def update_user(self, user: User) -> None:
        self.user_data[user.id] = user

    def create_user_id(self) -> str:
        return self.generate_unique_id(self.chat_data.keys())

    def chat_exists(self, chat_id: str) -> bool:
        return chat_id in self.chat_data
        
    def load_chat(self, chat_id: str) -> Chat: 
        
        return self.chat_data[chat_id]

    def create_chat(self, chat_id, user: User):
        chat = Chat(id=chat_id, user_id=user.id)
        user.add_chat_id(chat.id)
        return chat

    def create_chat_id(self) -> str: 
        return self.generate_unique_id(self.user_data.keys())

    def save_chat(self, chat: Chat) -> None:
        
        self.chat_data[chat.id] = chat

    def update_chat(self, chat: Chat) -> None: 
        self.chat_data[chat.id] = chat

    def save_session(self):
        user_json_data = {user_id: user_dict.convert_to_dict() for user_id, user_dict in self.user_data.items()}
        with open(self.user_json_path, 'w') as f:
            json.dump(user_json_data, f, indent=2, cls=utils.data.CustomEncoder)
        
        chat_json_data = {chat_id: user_dict.convert_to_dict() for chat_id, user_dict in self.chat_data.items()}
        with open(self.chat_json_path, 'w') as f:
            json.dump(chat_json_data, f, indent=2, cls=utils.data.CustomEncoder)
        logger.debug('Saved JSON.')

    @staticmethod
    def generate_unique_id(keys):
        unique_id = utils.data.generate_id()
        while unique_id in keys:
            unique_id = utils.data.generate_id()
        return unique_id



class SessionManager:
    def __init__(self):
        # TODO: Add switch to change JSON vs Mongo
        self.dao = SessionDataJSON()

    def get_chat_session(self, chat_id: str) -> Chat:
        chat = self.dao.get_chat(chat_id)
        return chat

    def create_chat_session(self, user_id: Union[str,None]) -> Chat:
        if user_id is None:
            user_id = self.dao.create_user_id()
        user = self.dao.get_user(user_id)

        chat_id = self.dao.create_chat_id()
        chat = self.dao.create_chat(chat_id, user)
        return chat

    def get_all_data(self):
        all_data = {
            'chats': self.chat_data,
            'users': self.user_data
        }
        
        return json.loads(json.dumps(all_data, cls=utils.data.CustomEncoder))


    def update_session_data(self, user_id, chat_id, chat: Chat):
        self.dao.save_chat(chat)
        # Probably don't want a generic save session, should save on changing the dao
        self.save_session()

    def save_session(self):
        self.dao.save_session()

    def get_user_ids(self):
        user_info = {}
        for user_id, user_obj in self.user_data.items():
            user_info[user_id] = {
                'created': user_obj.created,
                'num_chats': len(user_obj.chat_ids)
            }
        return user_info

    def remove_all_chats(self, user_id: str):
        chat_ids = self.user_data[user_id].chat_ids
        for chat_id in chat_ids:
            self.dao.remove_chat(chat_id)
        self.save_session()

    def remove_single_chat(self, user_id, chat_id: str):
        self.dao.remove_chat(chat_id)
        self.save_session()


    @property
    def chat_data(self):
        return self.dao.chat_data
    
    @property
    def user_data(self):
        return self.dao.user_data

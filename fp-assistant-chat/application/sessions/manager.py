import json
import os

from typing import Union

from application import utils
from application.models.chat import Chat
from application.models.session import SessionDataJSON

SESSION_DIR_PATH = os.path.join(os.path.dirname(__file__), 'data')

class SessionManager:
    def __init__(self):
        # TODO: Add switch to change JSON vs Mongo
        self.dao = SessionDataJSON(session_path=SESSION_DIR_PATH)

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

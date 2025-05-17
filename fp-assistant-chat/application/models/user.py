import datetime

from typing import Optional, List, Union

from application import utils
from application.models.chat import Chat

class User:
    id: str
    name: Optional[str]
    chat_ids: List[str]
    chats: List[Chat]
    created: datetime.datetime

    def __init__(self, id: str, name: Optional[str] = None, chat_ids=[], chats=[],
                 created: Optional[datetime.datetime] = None) -> None:
        if not isinstance(id, str):
            raise TypeError(f'id must be type str not {type(id)}')
        elif not (created is None or isinstance(created, datetime.datetime)):
            raise TypeError(f'created must be None or datetime.datetime, not {type(created)}')
        self.id = id
        self.name = name
        self.chat_ids = chat_ids
        self.chats = chats # Need to load in chats, may be expensive in future. Consider flag in function to load in all at once or wait until needed

        if created is None:
            self.created = datetime.datetime.now()
        else:
            self.created = created


    def convert_to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'chat_ids': self.chat_ids,
            'chats': self.chats,
            'created': utils.datetime.datetime_to_str(self.created),
        }

    def add_chat_id(self, chat_id: str):
        self.chat_ids.append(chat_id)

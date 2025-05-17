import datetime

from enum import Enum, auto
from typing import List, Optional, Union

from application import utils
from application.models.requests import Response

class ChatStage(Enum):
    CREATION = auto()
    QUERY = auto()
    EXPLAIN = auto()

class ChatLine:
    sender: str
    message: str
    timestamp: datetime.datetime
    response: Optional[Response] = None

    def __init__(self, sender, message, timestamp: Optional[Union[datetime.datetime, str]] = None, response: Response = None) -> None:
        self.sender = sender
        self.message = message

        if timestamp is None:
            self.timestamp = datetime.datetime.now()
        elif isinstance(timestamp, str):
            self.timestamp = utils.datetime.str_to_datetime(timestamp)
        else:
            self.timestamp = timestamp


        self.response = response
        
    
    def convert_to_dict(self):
        # TODO: save response to be able to load in
        return {
            'sender': self.sender,
            'message': self.message, 
            'timestamp': utils.datetime.datetime_to_str(self.timestamp)
        }

class Chat:
    """Chat session object that handles logic for an individual chat

    Attributes:
        id: chat ID used to identify unique chats
        name: chat name
        user_id: user id in chat
        history: chat history
        stage: current stage in the chat flow
        created: time when chat was created
    """
    id: str
    user_id: str
    name: Optional[str]
    history: List[ChatLine]
    stage: ChatStage
    stage_log: List[ChatStage]
    created: datetime.datetime

    def __init__(self, 
                 id: str, 
                 user_id: str, 
                 name: Optional[str] = None,
                 history: List[ChatLine] = [],
                 stage_log: List[ChatStage] = [],
                 stage: ChatStage = ChatStage.CREATION,
                 created: Optional[datetime.datetime] = None,
                ) -> None:
        if not isinstance(id, str):
            raise TypeError(f'id must be type str not {type(id)}')
        elif not (created is None or isinstance(created, datetime.datetime)):
            raise TypeError(f'created must be None or datetime.datetime, not {type(created)}')

        self.id = id
        self.user_id = user_id
        self.name = name
        self.history = history

        self._stage = stage
        
        if stage_log:
            self.stage_log = stage_log
        else:
            self.stage_log = [self.stage]
        
        if created is None:
            self.created = datetime.datetime.now()
        else:
            self.created = created



    def record_chat(self, sender, message, response=None):
        new_line = ChatLine(sender, message, response=response)
        self.history.append(new_line)


    def convert_to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'history': [chat_line.convert_to_dict() for chat_line in self.history],
            'stage_log': [stage.name for stage in self.stage_log],
            'stage': self.stage.name,
            'created': utils.datetime.datetime_to_str(self.created),

        }

    @property
    def stage(self):
        return self._stage
    
    @stage.setter
    def stage(self, value):
        if isinstance(value, ChatStage):
            self._stage = value
            self.stage_log.append(value)
        else:
            raise ValueError(f'Chat stage is being set incorrectly, update to ChatStage object.')

from __future__ import annotations
from typing import Optional, List

import logging

from application.openai_manager.constants import ENDPOINT
from application.openai_manager.defaults import MODEL

logger = logging.getLogger(__name__)

class PromptNode:
    """Handles all logic and maintenance needed for prompts
    """
    name: str
    base_prompt: str
    endpoint: str
    parent: Optional[PromptNode]
    redo: bool
    question: Optional[str]
    response: Optional[str]
    children: List[PromptNode]
    traverse: bool
    failed: bool
    

    def __init__(self, name, base_prompt, endpoint, extract_func=None, validation_func=None, model=None, parent=None, redo=True, question_text=None, custom_msg_func=None, traverse=True):
        """Creates object responsible for managing a single base prompt. 

        Args:
            name (str): name of prompt node
            base_prompt (str): text of base prompt
            endpoint (str): endpoint to use. Ideally, only use a value from openai_constants.ENDPOINT
            extract_func (callable, optional): function used to extract value from model response. Defaults to None. Currently not supported
            validation_func (callable, optional): function used to validate the extracted value from the model response. Defaults to None. Currently not supported.
            model (str, optional): name of model to use. Defaults to None.
            parent (PromptNode, optional): parent prompt. Used to build from base prompt Defaults to None.
            redo (bool, optional): flag to decide if prompt should be re-run if new information is given. Defaults to True.
            question_text (str, optional): question text used to ask for answer related to prompt. Defaults to None. 
            custom_msg_func (callable, optional): Function to craft message from prompt. Defaults to None. Currently not supported.
        """
        self.name = name
        self.base_prompt = base_prompt
        self.endpoint = endpoint
        
        self.parent = parent
        self.redo = redo
        self.question = question_text
        
        self.children = []
        self.response = None

        # Set up defaults:
        # Need model default?
        if not model:
            if self.endpoint == ENDPOINT.CHAT:
                model = MODEL.CHAT
            elif self.endpoint == ENDPOINT.COMPLETION:
                model = MODEL.COMPLETION
            else:
                ValueError(f'Cannot set model for endpoint {self.endpoint} for object {self} since it does not exist.')
        self.model = model

        # Passing functions along
        self.extract_func = extract_func
        self.custom_msg_func = custom_msg_func

        if self.parent:
            self.parent.__add_child(self)

        self.traverse = traverse
        self.failed = False

    def build_prompt(self, text=None) -> List[str]:
        """Builds prompts in a list and returns. Base class will return a single item. Can override to return multiple prompts

        Note: arg `text` is only used if parent is not None and text is not supplied.

        Args:
            text (str, optional): Text to be used. Defaults to None.

        Returns:
            List[str]: list of prompts to use.
        """
        # Could convert to property if we set original_text to parent node intiailly.
        # Then we could use a recursive function to get original_text of parent. 

        # Only need text for first prompt, all others will be passed
        if text is None and self.parent is not None:
            text = self.parent.response
        
        return [self.base_prompt + text + '\n\nCOMPLETION\n']

    def reset_response(self, reset_parent=True):
        """Reset response to None and can trigger parent to do same

        Args:
            reset_parent (bool, optional): flag to decide if parent should be reset too. Defaults to True.
        """
        # Run when 
        if self.redo and self.response is not None:
            # Potentially could store old responses in "self.responses" later on
            self.response = None

        # Call function on parent to reset 
        if self.parent and reset_parent:
            self.parent.reset_response()


    def extract_response(self):
        """Uses `extract_func` to parse response.

        Returns:
            any: Value extracted from response
        """
        # Assume extraction also validaties?
        if self.response and self.extract_func:
            extracted_value = self.extract_func(self.response)
            return  extracted_value
        return None


    def __add_child(self, child: PromptNode):
        """Add child to list of children.

        Args:
            child (PromptNode): child node to be added
        """
        self.children.append(child)
    
    def __str__(self):
        return f'PromptNode({self.name})'

    def __repr__(self) -> str:
        return self.__str__()

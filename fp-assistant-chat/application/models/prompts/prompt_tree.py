import logging
import re

from typing import Union, List, Dict

from application.models.prompts.prompt_nodes import PromptNode

logger = logging.getLogger(__name__)
class PromptTree:
    root: List[PromptNode]
    name2prompt: Dict[str, PromptNode]
    leafs: List[PromptNode]
    all_nodes: List[PromptNode]
    question_nodes: List[PromptNode]

    def __init__(self, root: Union[PromptNode, List[PromptNode]]) -> None:
        # Assume root is a list of at least one node
        if isinstance(root, PromptNode):
            root = [root]
        self.root = root
        self.name2prompt = {}
        self.leafs = []
        self.all_nodes = []
        self.question_nodes = []
        # self.stages = self.build_prompt_stages()
        self.init_traversal()

    def init_traversal(self):
        name2prompt = {}
        leaf_nodes = []
        all_nodes = []
        question_nodes = []
        nodes = self.root
        while nodes:
            new_nodes = []
            for node in nodes:
                all_nodes.append(node)
                name2prompt[node.name] = node
                if node.children:
                    new_nodes.extend(node.children)
                else:
                    leaf_nodes.append(node)
                if node.question is not None:
                    question_nodes.append(node)
            nodes = new_nodes
        
        # Set variables from traversal results
        self.name2prompt = name2prompt
        self.leafs = leaf_nodes
        self.all_nodes = all_nodes
        self.question_nodes = question_nodes

    def generate_question_list(self):
        questions = []
        for question_node in self.question_nodes:
            if question_node.response is None:
                questions.append(question_node.question)
        return questions


    def reset_response_path(self, node_name):
        node = self.name2prompt[node_name]
        node.reset_response()


    def get_responses(self):
        responses = {}
        nodes = self.root
        while nodes:
            new_nodes = []
            for node in nodes:
                responses[node.name] = node.response
                new_nodes.extend(node.children)
            nodes = new_nodes
        return responses
                
    
    def build_prompt_stages(self):
        # Greedy approach - minimizes number of async stages, potentially run prompts not needed
        stages = []
        stages.append(self.root)
        curr_stage = stages[-1]
        while curr_stage:
            new_nodes = []

            for node in curr_stage:
                if node.children:
                    new_nodes.extend(node.children)

            if new_nodes:
                stages.append(new_nodes)
                curr_stage = stages[-1]
            else:
                break
        
        return stages

    def get_prompt_batch(self, prompt_text):
        # This version starts from the top and collects all promtps ready to be asked.
        nodes = self.root
        prompts = {}
        while nodes:
            new_nodes = []
            for node in nodes:
                if node.response is None and node.traverse:
                    text = prompt_text if node.parent is None else None
                    built_prompts = node.build_prompt(text)
                    if len(built_prompts) == 0:
                        continue
                    elif len(built_prompts) == 1:
                        prompts[node.name] = {
                            'prompt': built_prompts[0],
                            'endpoint': node.endpoint,
                            'model': node.model
                            }
                    else:
                        # Set up response
                        node.response = [None] * len(built_prompts)
                        for i, built_prompt in enumerate(built_prompts):
                            prompts[f'{node.name}.{i}'] = {
                                'prompt': built_prompt,
                                'endpoint': node.endpoint,
                                'model': node.model
                            }
                elif node.traverse:
                    new_nodes.extend(node.children)
                else:
                    logger.debug(f'Not checking children of {node} because traverse is False.')
            nodes = new_nodes

        return prompts

    def get_response(self, node_name, default_value=''):
        if node_name not in self.name2prompt:
            return default_value
        
        prompt = self.name2prompt[node_name]
        if prompt.response is None:
            return default_value
        else:
            return prompt.response


    def set_response(self, node_name: str, response_text: str):
        if re.search(r'\.\d+$', node_name):
            node_name, prompt_idx = node_name.rsplit('.')
            prompt_idx = int(prompt_idx)
            node = self.name2prompt[node_name].response[prompt_idx] = response_text
        else:
            self.name2prompt[node_name].response = response_text

    @property
    def complete(self):
        # Assumes that if all leafs are set, then prompting is done.
        for node in self.leafs:
            if isinstance(node.response, list):
                if any([resp is None for resp in node.response]):
                    return False
            if node.response is None:
                return False
        else:
            return True
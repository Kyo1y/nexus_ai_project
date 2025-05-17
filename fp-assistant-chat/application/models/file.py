
from string import Template
from typing import Optional

from application import utils
from application.configs import config


class File:
    text: str
    is_template: bool
    def __init__(self, path: str, load: Optional[bool] = None, is_template: Optional[bool] = None):
        """Instance of a file object

        Args:
            path (str): path to file
            is_template (Optional[bool], optional): Whether or not the given file is a template. If None, will automatically decide based on prescence of special chatacter "$". Defaults to None.
            load (Optional[bool], optional): Whether or not to keep text in memory or to read it in each time. If None, defaults to config setting. Defaults to None.
        """
        self.path = path

        if load is None:
            load = config.LOAD_FILES
        self.load = load

        # Only keep text in memory upon request
        if self.load:
            self._text = self.load_text()
        else:
            self._text = None

        # Helpful attribute
        if is_template is None:
            is_template = '$' in self.text
        self.is_template = is_template

    @property
    def text(self):
        if self._text:
            return self._text
        else:
            return self.load_text()

    def load_text(self):
        text = utils.os.load_file(self.path)
        text = text.strip()
        return text
    
    def substitute(self, **kwargs) -> str:
        template = Template(self.text)
        subbed_text = template.substitute(**kwargs)
        return subbed_text
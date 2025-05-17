from string import Template

from utils.os import load_file

def get_template(template_path):
    """Load and return the string template at the specified path.

    Args:
        template_path (str): The path to the template file.

    Returns:
        string.Template: A string template object.
    """

    txt = load_file(template_path)
    template = Template(txt)
    return template
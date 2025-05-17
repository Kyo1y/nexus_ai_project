import json
import logging

logger = logging.getLogger(__name__)

def load_file(file_path):
    """Loads file given path. Only supports JSON and txt files.

    Args:
        file_path (str): path to file

    Returns:
        str: file
    """
    logger.debug('Loading file: {}'.format(file_path))
    file_ext = file_path.split('.')[-1].lower()
    if file_ext in ['txt', 'ftl']:
        with open(file_path, 'r') as f:
            file = f.read()
        return file
    elif file_ext == 'json':
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    else:
        # TODO: add some other functionality when prompt can't be loaded properly
        logging.error(f'ERROR: Could not load file: {file_path}')
        return None

def save_file(file_path, object, **kwargs):
    """Saves object to desired path. This method is set up to take in additional keyword arguments to pass to writing function.

    Args:
        file_path (str): path for file
        object (Any): file to be saved to given file
    """
    file_ext = file_path.split('.')[-1].lower()
    if file_ext == 'txt':
        with open(file_path, 'w') as f:
            f.write(object)
    elif file_ext == 'json':
        with open(file_path, 'w') as json_file:
            json.dump(object, json_file, **kwargs)
    else:
        logging.error(f'ERROR: Could not write to file {file_path}')


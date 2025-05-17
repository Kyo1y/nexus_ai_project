import uuid

from json import JSONEncoder

def generate_id():
    session_id = str(uuid.uuid4())
    return session_id

class CustomEncoder(JSONEncoder):
    def default(self, o):
        if getattr(o, 'convert_to_dict', None) is not None:
            return o.convert_to_dict()
        else:
            return o.__dict__

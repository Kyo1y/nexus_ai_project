from application.chat import manager

def get_initial_chat():
    user_id = 'abc-123'
    opening_text, chat_id, uid = manager.create_chat(user_id)
    return opening_text, chat_id , uid

def get_response(chat_id, input_text, user_id):
    chat_resp = manager.continue_chat(user_id, chat_id, input_text)
    return chat_resp
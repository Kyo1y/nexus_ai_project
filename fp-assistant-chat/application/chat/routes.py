
import logging

from flask import session, request
from flask_cors import cross_origin

from application.chat import chat_bp
from application.chat import manager
from application.chat import outputter

logger = logging.getLogger(__name__)

@chat_bp.route('/', methods=['GET'])
@cross_origin()
def create_chat():
    user_id = session.get('user_id', None)

    message, chat_id, user_id = manager.create_chat(user_id)

    if 'user_id' not in session:
        session['user_id'] = user_id
        logger.debug(f'Updated user_id to {user_id} in session object.')
    
    return {'chat': message, 'chat_id': chat_id}, 200

@chat_bp.route('/<chat_id>', methods=['POST'])
@cross_origin()
def continue_chat(chat_id):
    user_id = session.get('user_id', None)
    try:
        input_json = request.get_json()
        text = input_json.get('chat', '')
        identity = input_json.get('identity', None)
        response_dict, response_code = manager.continue_chat(user_id, chat_id, text, identity)
        if 'response_obj' in response_dict:
            del response_dict['response_obj']
        if 'columns' in response_dict:
            del response_dict['columns']
        return response_dict, response_code
    except Exception as e:
        logger.exception('Unable to continue chat')
        message = outputter.build.error()
        return {'chat': message}, 201

@chat_bp.route('/test', methods=['GET'])
def chat_create():
    if 'testID' in session:
        logger.info('testID in session')
    else:
        logger.info('New user, saving ID')
        session['testID'] = 'my-id'
    return 'Test endpoint sucessful', 200

@chat_bp.route('/canned', methods=['GET'])
@cross_origin()
def canned_examples():
    return {'examples': [
        {
            '_id': 1, 
            'promptName': 'Date Filter',
            'query': 'Which active agents haven\'t written a policy since the beginning of last year?'
        },
        {
            '_id': 2,
            'promptName': 'Average Face Amount with Count Constraint',
            'query': 'Which agents have written more than 5 policies since January 1st? What are their average face amounts?'
        }, 
        {
            '_id': 3,
            'promptName': 'Face Amount and Date Filter',
            'query': 'Show me all agents with a policy that has a face amount over $1 mil since January 1st 2024'
        },
        {
            '_id': 4,
            'promptName': 'Total Policy Count',
            'query' : 'Show me the number of pending policies agents have written since Jan 1st 2024'
        }, 
        {
            '_id': 5,
            'promptName': 'Aggregate Filters',
            'query' : 'Show me the total annual premiums of all agents who issued polices between jan 1st 2023 and jan 1st 2024. filter out agents who have less than 2 policies in that time frame and max face amount greater than 500000'
        },
        {
            '_id': 6,
            'promptName': 'High Performers',
            'query': 'Which agents have written at least 10 policies over 2 million in the past year?'
        },
        {
            '_id': 7,
            'promptName': 'Premium Aggregation',
            'query': 'Aggregate all premiums for all agents, give me top 10'
        }, 
        {
            '_id': 8,
            'promptName': 'High Volume',
            'query': 'Show me everyone with an abnormally high business volume'
        }
        ]}

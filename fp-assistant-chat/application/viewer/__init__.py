import json
import logging

from flask import Blueprint, render_template, request, session, jsonify

from application.viewer.run_chat import get_initial_chat, get_response
from application.utils.data import CustomEncoder

logger = logging.getLogger(__name__)

viewer_bp = Blueprint('viewer', __name__, template_folder='templates', static_folder='static')

@viewer_bp.route('/')
def index_page():
    initial_message, chat_id, user_id = get_initial_chat()
    session['viewer_chat_id'] = chat_id
    session['viewer_user_id'] = user_id
    return render_template('app.html', initial_message=initial_message)

@viewer_bp.route('/backend', methods=['POST'])
def backend_continue_chat():
    request_json = request.get_json()
    logger.info('Recieved request to backend')
    input_text = request_json.get('message', '')
    chat_id = session['viewer_chat_id']
    user_id = session['viewer_user_id']
    if input_text:
        try:
            logger.info('Sending data for extraction')
            chat_resp, code = get_response(chat_id, input_text, user_id)
            display_table = chat_resp['display_table']
            if display_table:
                columns = chat_resp['columns']
                # Set up columns
                render_cols = ['Agent Name']
                if 'previous_performance' in columns:
                    render_cols.append('Historical Average')
                if 'current_performance' in columns:
                    render_cols.append('Current Business Volume')
                if 'label' in columns:
                    render_cols.append('Performance Against Norm')
                if 'confidence' in columns:
                    render_cols.append('Confidence')
                if 'last_policy_date' in columns:
                    render_cols.append('Last Policy Date')
                if 'recent_faceamount' in columns:
                    render_cols.append('Max Face Amount')
                # Format rows
                agents = [agent.row() for agent in chat_resp['response_obj'].results]
                html_table = render_template('base_table.html', agents=agents, columns=render_cols)
                chat_resp.update({'html_table': html_table, 'columns': render_cols})
                # Can't return response object without errors
                del chat_resp['response_obj']
            
            return chat_resp, code
        except Exception as e:
            logger.exception('Exception occured')
            return {'output': 'Exception occured when processing.'}, 201
    return {'output': 'Unable to fulfill request.'}, 200


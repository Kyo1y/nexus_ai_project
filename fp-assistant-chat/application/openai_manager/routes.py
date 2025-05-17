from flask import Blueprint, request

from application.openai_manager.key_manager import key_manager

api_manager_bp = Blueprint('api_manager', __name__)

@api_manager_bp.route('/change-key', methods=['POST'])
def change_key():
    request_json = request.get_json()
    new_key = request_json['key']
    key_manager.current_key = new_key
    return 'Key updated', 200

@api_manager_bp.route('/check-key', methods=['GET'])
def check_key():
    return key_manager.current_key, 200

@api_manager_bp.route('/change-mode', methods=['POST'])
def change_mode():
    request_json = request.get_json()
    new_mode = request_json['mode']
    key_manager.mode = new_mode
    return 'Mode updated', 200

@api_manager_bp.route('/check-mode', methods=['GET'])
def check_mode():
    return key_manager.mode, 200

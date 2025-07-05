from flask import Blueprint, jsonify
from ..controllers.user_controller import get_users

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
def list_users():
    return get_users()

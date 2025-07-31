from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..controllers.user_controller import get_users, login_users, protected_users
from flasgger.utils import swag_from

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/users/get_users.yaml')
def list_users():
    return get_users()

@user_bp.route('/login', methods=['POST'])
@swag_from('../swagger_docs/auth/login.yaml')
def handle_login_users():
    return login_users()

@user_bp.route('/protected', methods=['GET'])
@jwt_required()
def handle_protected_users():
    return protected_users()


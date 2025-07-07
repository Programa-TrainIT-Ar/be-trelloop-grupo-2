from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..controllers.user_controller import get_users, login_users

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
def list_users():
    return get_users()


@user_bp.route('/login', methods=['POST'])
def handle_login_users():
    return login_users()


#USO DE VERIFICACION DEL TOKEN USANDO @jwt_required()
## from flask_jwt_extended import jwt_required
# # @user_bp.route('/login', methods=['POST'])
# # @jwt_required()
# # def handle_login_users():
# #     return login_users()


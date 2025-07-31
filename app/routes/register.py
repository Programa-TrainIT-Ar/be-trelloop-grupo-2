from flask import Blueprint, jsonify, request
from app.controllers.user_controller import register_user
from flasgger.utils import swag_from

register_bp = Blueprint('register', __name__, url_prefix='/api')

@register_bp.route('/register', methods=['POST'])
@swag_from('../swagger_docs/auth/register.yaml')
def register():
    data = request.json
    return register_user(data)

@register_bp.route("/register", methods=["GET"])
def debug_register():
    return "Ruta /api/register disponible para POST", 200
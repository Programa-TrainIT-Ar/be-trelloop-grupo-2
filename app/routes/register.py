from flask import Blueprint, jsonify, request
from app.controllers.user_controller import register_user

register_bp = Blueprint('register', __name__, url_prefix='/api')

@register_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint para registrar un nuevo usuario.
    """
    data = request.json
    return register_user(data)

@register_bp.route("/register", methods=["GET"])
def debug_register():
    return "Ruta /api/register disponible para POST", 200
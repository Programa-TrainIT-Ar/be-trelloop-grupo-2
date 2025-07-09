from flask import Blueprint
from app.controllers.user_controller import register_user

register_bp = Blueprint('register', __name__)

@register_bp.route('/api/register', methods=['POST'])
def register():
    """
    Endpoint para registrar un nuevo usuario.
    """
    return register_user()
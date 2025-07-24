from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..controllers.board_controller import create_board

board_bp = Blueprint('board', __name__, url_prefix='/api/boards')


@board_bp.route('/', methods=['POST'])
@jwt_required()
def handle_create_board():
    return create_board()


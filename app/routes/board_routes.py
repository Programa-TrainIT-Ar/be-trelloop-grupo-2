from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..controllers.board_controller import create_board, get_all_boards, get_board_by_id, get_boards_by_user

board_bp = Blueprint('board', __name__, url_prefix='/api/boards')


@board_bp.route('/', methods=['POST'])
@jwt_required()
def handle_create_board():
    return create_board()

@board_bp.route('/', methods=['GET'])
@jwt_required()
def handle_get_all_boards():
    return get_all_boards()

@board_bp.route('/<int:board_id>', methods=['GET'])
@jwt_required()
def handle_get_board_by_id(board_id):
    return get_board_by_id(board_id)

@board_bp.route('/member', methods=['GET'])
@jwt_required()
def handle_get_my_boards():
    return get_boards_by_user()
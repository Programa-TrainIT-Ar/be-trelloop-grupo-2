from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..controllers.board_controller import create_board, get_all_boards, get_board_by_id, get_boards_by_user, update_board, delete_board

board_bp = Blueprint('board', __name__, url_prefix='/api/boards')


@board_bp.route('/', methods=['POST'])
@jwt_required()
def handle_create_board():
    return create_board()

@board_bp.route('/', methods=['GET'])
def handle_get_all_boards():
    return get_all_boards()

@board_bp.route('/<int:board_id>', methods=['GET'])
def handle_get_board_by_id(board_id):
    return get_board_by_id(board_id)

@board_bp.route('/member', methods=['GET'])
@jwt_required()
def handle_get_my_boards():
    return get_boards_by_user()

@board_bp.route('/<int:board_id>', methods=['PUT'])
@jwt_required()
def handle_update_board(board_id):
    return update_board(board_id)

@board_bp.route('/<int:board_id>', methods=['DELETE'])
@jwt_required()
def handle_delete_board(board_id):
    return delete_board(board_id)
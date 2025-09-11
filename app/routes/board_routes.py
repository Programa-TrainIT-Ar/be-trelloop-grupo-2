from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flasgger.utils import swag_from
from ..controllers.board_controller import (create_board, 
get_all_boards, 
get_board_by_id, 
get_boards_by_user, 
update_board, 
delete_board, 
toggle_favorite, 
add_member,
remove_member,
update_member_role)

board_bp = Blueprint('board', __name__, url_prefix='/api/boards')


@board_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from('../swagger_docs/boards/create_board.yaml')
def handle_create_board():
    return create_board()

@board_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/boards/get_all_boards.yaml')
def handle_get_all_boards():
    return get_all_boards()

@board_bp.route('/<int:board_id>', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/boards/get_board_by_id.yaml')
def handle_get_board_by_id(board_id):
    return get_board_by_id(board_id)

@board_bp.route('/member', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/boards/get_my_boards.yaml')
def handle_get_my_boards():
    return get_boards_by_user()

@board_bp.route('/<int:board_id>', methods=['PUT'])
@jwt_required()
@swag_from('../swagger_docs/boards/update_board.yaml')
def handle_update_board(board_id):
    return update_board(board_id)

@board_bp.route('/<int:board_id>', methods=['DELETE'])
@jwt_required()
@swag_from('../swagger_docs/boards/delete_board.yaml')
def handle_delete_board(board_id):
    return delete_board(board_id)

@board_bp.route('/<int:board_id>/favorite', methods=['PATCH'])
@jwt_required()
def handle_toggle_favorite(board_id):
    return toggle_favorite(board_id)

@board_bp.route('/<int:board_id>/members', methods=['POST'])
@jwt_required()
def handle_add_member(board_id):
    return add_member(board_id)

@board_bp.route('/<int:board_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def handle_remove_member(board_id, member_id):
    return remove_member(board_id, member_id)

@board_bp.route('/<int:board_id>/members/<int:member_id>/role', methods=['PUT'])
@jwt_required()
def handle_update_member_role(board_id, member_id):
    return update_member_role(board_id, member_id)

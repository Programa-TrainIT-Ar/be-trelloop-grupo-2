from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flasgger.utils import swag_from
from ..controllers.list_controller import get_lists_by_board, create_list, delete_list

list_bp = Blueprint('list', __name__, url_prefix='/api/boards')


@list_bp.route('/<int:board_id>/lists', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/lists/get_lists_by_board.yaml')
def handle_get_lists_by_board(board_id):
    return get_lists_by_board(board_id)

@list_bp.route('/<int:board_id>/lists', methods=['POST'])
@jwt_required()
@swag_from('../swagger_docs/lists/create_list.yaml')
def handle_create_list(board_id):
    return create_list(board_id)

@list_bp.route('/<int:board_id>/lists/<int:list_id>', methods=['DELETE'])
@jwt_required()
def handle_delete_list(board_id, list_id):
    return delete_list(board_id, list_id)

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flasgger.utils import swag_from
from ..controllers.card_controller import create_card, get_cards_by_list, update_card, delete_card, get_card_by_id

card_bp = Blueprint('card', __name__, url_prefix='/api/boards')

@card_bp.route('/<int:board_id>/lists/<int:list_id>/cards', methods=['POST'])
@jwt_required()
@swag_from('../swagger_docs/cards/create_card.yaml')
def handle_create_card(board_id, list_id):
    return create_card(board_id, list_id)

@card_bp.route('/<int:board_id>/lists/<int:list_id>/cards', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/cards/get_cards_by_list.yaml')
def handle_get_cards_by_list(board_id, list_id):
    return get_cards_by_list(board_id, list_id)

@card_bp.route('/<int:board_id>/lists/<int:list_id>/cards/<int:card_id>', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/cards/get_card_by_id.yaml')
def handle_get_card_by_id(board_id, list_id, card_id):
    return get_card_by_id(board_id, list_id, card_id)

@card_bp.route('/<int:board_id>/lists/<int:list_id>/cards/<int:card_id>', methods=['PUT'])
@jwt_required()
@swag_from('../swagger_docs/cards/update_card.yaml')
def handle_update_card(board_id, list_id, card_id):
    return update_card(board_id, list_id, card_id)

@card_bp.route('/<int:board_id>/lists/<int:list_id>/cards/<int:card_id>', methods=['DELETE'])
@jwt_required()
@swag_from('../swagger_docs/cards/delete_card.yaml')
def handle_delete_card(board_id, list_id, card_id):
    return delete_card(board_id, list_id, card_id)
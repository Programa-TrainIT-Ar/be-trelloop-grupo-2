from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flasgger.utils import swag_from
from ..controllers.comment_controller import create_comment, get_comments_by_card

comment_bp = Blueprint('comment', __name__, url_prefix='/api/boards')

@comment_bp.route('/<int:board_id>/lists/<int:list_id>/cards/<int:card_id>/comments', methods=['POST'])
@jwt_required()
@swag_from('../swagger_docs/comments/create_comment.yaml')
def handle_create_comment(board_id, list_id, card_id):
    return create_comment(board_id, list_id, card_id)

@comment_bp.route('/<int:board_id>/lists/<int:list_id>/cards/<int:card_id>/comments', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/comments/get_comments_by_card.yaml')
def handle_get_comments_by_card(board_id, list_id, card_id):
    return get_comments_by_card(board_id, list_id, card_id)



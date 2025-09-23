from app.models.board import Board
from app.models.card import Card, CardComment
from app.models.list import List
from app.models.relationships import UserBoard
from app.database.database import db
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from ..logs.logger import logger

def create_comment(board_id, list_id, card_id):
    """
    Crear un nuevo comentario en una tarjeta.
    - La tarjeta debe pertenecer a la lista y al tablero
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        comment_text = data.get("comment", "").strip()
        if not comment_text:
            return jsonify({"error": "El campo 'comment' es requerido"}), 400

        # Verificar acceso al tablero
        board = (
            db.session.query(Board)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id, Board.id == board_id)
            .first()
        )
        if not board:
            return jsonify({"error": f"Tablero {board_id} no encontrado o sin acceso"}), 404

        # Verificar que la lista existe en el tablero
        target_list = (
            db.session.query(List)
            .filter_by(id=list_id, board_id=board_id)
            .first()
        )
        if not target_list:
            return jsonify({"error": f"Lista {list_id} no encontrada en el tablero"}), 404

        # Verificar que la tarjeta existe en la lista
        card = (
            db.session.query(Card)
            .filter_by(id=card_id, list_id=list_id)
            .first()
        )
        if not card:
            return jsonify({"error": f"Tarjeta {card_id} no encontrada en la lista {list_id}"}), 404

        # Crear comentario
        new_comment = CardComment(
            card_id=card_id,
            user_id=user_id,
            comment=comment_text
        )

        db.session.add(new_comment)
        db.session.commit()
        db.session.refresh(new_comment)

        logger.info(f"Comentario creado en tarjeta {card_id} de lista {list_id} por usuario {user_id}")

        return jsonify({
            "success": True,
            "message": "Comentario creado exitosamente",
            "comment": new_comment.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error al crear comentario en tarjeta {card_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

def get_comments_by_card(board_id, list_id, card_id):
    """
    Obtener todos los comentarios de una tarjeta
    dentro de una lista y un tablero específicos.
    """
    try:
        user_id = int(get_jwt_identity())

        # Verificar acceso al tablero
        board = (
            db.session.query(Board)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id, Board.id == board_id)
            .first()
        )
        if not board:
            return jsonify({"error": f"Tablero {board_id} no encontrado o sin acceso"}), 404

        # Verificar lista
        target_list = (
            db.session.query(List)
            .filter_by(id=list_id, board_id=board_id)
            .first()
        )
        if not target_list:
            return jsonify({"error": f"Lista {list_id} no encontrada en el tablero"}), 404

        # Verificar tarjeta
        card = (
            db.session.query(Card)
            .filter_by(id=card_id, list_id=list_id)
            .first()
        )
        if not card:
            return jsonify({"error": f"Tarjeta {card_id} no encontrada en la lista {list_id}"}), 404

        # Obtener comentarios ordenados por fecha
        comments = (
            db.session.query(CardComment)
            .filter_by(card_id=card_id)
            .order_by(CardComment.created_at.desc())
            .all()
        )

        return jsonify({
            "success": True,
            "card_title": card.title,
            "comments": [c.to_dict() for c in comments]
        }), 200

    except Exception as e:
        logger.error(f"Error al obtener comentarios de tarjeta {card_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

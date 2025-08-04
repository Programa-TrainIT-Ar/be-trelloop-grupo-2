from app.models.board import Board
from app.models.list import List
from app.models.relationships import UserBoard
from app.database.database import db
from flask import jsonify ,request
from flask_jwt_extended import get_jwt_identity
from ..logs.logger import logger

def get_lists_by_board(board_id):
    try:
        user_id = int(get_jwt_identity())

        searched_board = (
            db.session.query(Board)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id, Board.id == board_id)
            .first()
        )

        if searched_board is None:
            return jsonify({"error": f"El tablero con id: {board_id} no fue encontrado"}), 404
        lists = List.query.filter_by(board_id=board_id).order_by(List.position).all()

        if not lists:
            return jsonify({
                "message": "El tablero no tiene listas creadas",
                "lists": []
            }), 200
        
        return jsonify([lista.to_dict() for lista in lists]), 200

    except Exception as e:
        logger.error(f"Error al obtener las listas del tablero {board_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error al obtener las listas"
        }), 500

def create_list(board_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        name = data.get("name")
        side = data.get("side", "right")
        side = side.lower() if isinstance(side, str) else ""

        if not name or side not in ("left", "right"):
            return jsonify({"error": "Campos requeridos: name y side (left o right)"}), 400
        
        board = (
            db.session.query(Board)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id, Board.id == board_id)
            .first()
        )

        if not board:
            return jsonify({"error": f"El tablero con id {board_id} no fue encontrado o no tienes acceso"}), 404

        last_list = (
            db.session.query(List)
            .filter_by(board_id=board_id)
            .order_by(List.position.desc())
            .first()
        )
        if not last_list:
            new_position = 0
        elif side == "right":
            new_position = last_list.position + 1
        elif side == "left":
            new_position = last_list.position


        db.session.query(List).filter(
                List.board_id == board_id,
                List.position >= new_position
            ).update({List.position: List.position + 1})
       
        new_list = List(name=name, position=new_position, board_id=board_id)
        db.session.add(new_list)
        db.session.commit()

        return jsonify(new_list.to_dict()), 201

    except Exception as e:
        logger.error(f"Error al crear la lista en el tablero {board_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500
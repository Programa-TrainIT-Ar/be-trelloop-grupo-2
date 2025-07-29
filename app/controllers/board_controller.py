from app.models.user import User
from app.models.board import Board
from app.models.tag import Tag
from app.models.relationships import UserBoard
from app.database.database import db
from flask import jsonify ,request
from flask_jwt_extended import get_jwt_identity
from ..logs.logger import logger

#CRUD FOR BOARD

def create_board():
    data= request.json
    try:
        user_id = int(get_jwt_identity())
        name = data.get("name", None)
        description = data.get("description")
        owner_id = user_id
        status = data.get("status", "PRIVATE").upper()
        board_image_url = data.get("boardImageUrl")
        tag_names = data.get('tags', [])
        member_ids = data.get('members', [])

        if not name:
            return jsonify({'error': f"Faltan campos obligatorios 'name'" }), 400

        new_board = Board(
            name=name,
            description=description,
            owner_id=owner_id,
            status=status,
            board_image_url=board_image_url
        )

        for user_id in member_ids:
            user = User.query.get(user_id)
            if user and user.id != owner_id:  
                new_board.members.append(user)
        
        owner = User.query.get(owner_id)
        if owner and owner.id not in new_board.members:
            new_board.members.append(owner)

        db.session.add(new_board)
        
        for tag_name in tag_names:
            tag_name = tag_name.strip().lower()
            if not tag_name:
                continue
            
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)

            new_board.tags.append(tag)
    
        db.session.commit()
        
        logger.info(f"Tabla creada exitosamente: {new_board.name}")

        return jsonify({
            "success": True,
            "message": "Tabla creada exitosamente",
        }), 201
    
    except Exception as e:
        logger.error(f"Error al crear tabla: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error al crear una tabla"}), 500


def get_all_boards():
    try:
        boards = Board.query.all()
        board_list = [board.to_dict() for board in boards]
        return jsonify(board_list), 200
    except Exception as e:
        logger.error(f"Error al obtener boards: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error al obtener las boards"
        }), 500

def get_board_by_id(board_id):
    try:
        board = Board.query.get(board_id)
        if board is None:
            return jsonify({
                "success": False,
                "message": "Board no encontrada"
            }), 404
        return jsonify(board.to_dict()), 200
    except Exception as e:
        logger.error(f"Error al obtener board: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error al obtener la board"
        }), 500
        
def get_boards_by_user():
    try:
        user_id = int(get_jwt_identity())
        logger.info(f"🔑 Usuario autenticado con ID: {user_id}")
        boards = (
            db.session.query(Board.id, Board.name, Board.created_at)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id)
            .all()
        )

        if not boards:
            return jsonify({
                "message": "No perteneces a ningún tablero.",
                "boards": []
            }), 200

        board_list = [
            {
                "id": b.id,
                "name": b.name,
                "created_at": b.created_at.isoformat()
            } for b in boards
        ]

        return jsonify({"boards": board_list}), 200

    except Exception as e:
        logger.error(f"Error al obtener tableros del usuario: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error al obtener tus tableros"
        }), 500
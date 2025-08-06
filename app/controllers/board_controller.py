from app.models.user import User
from app.models.board import Board
from app.models.tag import Tag
from app.models.relationships import UserBoard
from app.database.database import db
from flask import jsonify ,request
from flask_jwt_extended import get_jwt_identity
from ..logs.logger import logger
from ..utils.cloudinary_uploader import upload_image_to_cloudinary
from flask import abort
from flask_jwt_extended import jwt_required

#CRUD FOR BOARD

def create_board():
    try:
        # Soporta JSON o multipart/form-data
        if request.content_type and request.content_type.startswith("multipart/form-data"):
            data = request.form
            image_file = request.files.get("image")
            if image_file:
                board_image_url = upload_image_to_cloudinary(image_file)
            else:
                board_image_url = None
        else:
            data = request.get_json()
            board_image_url = data.get("boardImageUrl")

        user_id = int(get_jwt_identity())
        name = data.get("name")
        description = data.get("description")
        owner_id = user_id
        status = data.get("status", "PRIVATE").upper()
        tag_names = data.getlist('tags') if request.content_type.startswith("multipart/form-data") else data.get('tags', [])
        member_ids = data.getlist('members') if request.content_type.startswith("multipart/form-data") else data.get('members', [])

        if not name:
            return jsonify({'error': "Faltan campos obligatorios 'name'"}), 400

        new_board = Board(
            name=name,
            description=description,
            owner_id=owner_id,
            status=status,
            board_image_url=board_image_url
        )

        for uid in member_ids:
            user = User.query.get(uid)
            if user and user.id != owner_id:
                new_board.members.append(user)

        owner = User.query.get(owner_id)
        if owner and owner.id not in [u.id for u in new_board.members]:
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
            "message": "Error al crear una tabla"
        }), 500


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
        db.session.query(Board)
        .join(UserBoard, UserBoard.board_id == Board.id)
        .filter(UserBoard.user_id == user_id)
        .order_by(Board.created_at.asc())  # Mantiene orden estable por fecha de creación
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
                "boardImageUrl": b.board_image_url,
                "description": b.description,
                "members": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "lastName": m.last_name  
                    } for m in b.members
                ],
                "is_favorite": any(
                ub.user_id == user_id and ub.is_favorite
                for ub in b.userboard_relationships if ub.board_id == b.id
                ),
                "lists": [
                    {
                        "id": l.id,
                        "title": l.name,
                        "position": l.position
                    } for l in b.lists
                ],
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
    
def update_board(board_id):
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

        # Soporta JSON o multipart/form-data
        if request.content_type and request.content_type.startswith("multipart/form-data"):
            data = request.form
            image_file = request.files.get("image")
            if image_file:
                new_board_image_url = upload_image_to_cloudinary(image_file)
            else:
                new_board_image_url = None
        else:
            data = request.get_json()
            new_board_image_url = data.get("boardImageUrl")

        if not data:
            return jsonify({"error": "Los datos no fueron provistos"}), 400

        new_name = data.get("name")
        new_description = data.get("description")
        new_status = data.get("status", "PRIVATE").upper()
        new_tag_names = data.getlist('tags') if request.content_type.startswith("multipart/form-data") else data.get('tags', [])
        new_member_ids = data.getlist('members') if request.content_type.startswith("multipart/form-data") else data.get('members', [])

        if new_status not in ["PRIVATE", "PUBLIC"]:
            return jsonify({"error": "El status debe ser PRIVATE o PUBLIC"}), 400

        if not isinstance(new_tag_names, list):
            return jsonify({"error": "Tags debe ser una lista"}), 400
        if not isinstance(new_member_ids, list):
            return jsonify({"error": "Members debe ser una lista"}), 400

        if new_name:
            searched_board.name = new_name
        if new_description:
            searched_board.description = new_description
        if new_board_image_url:
            searched_board.board_image_url = new_board_image_url

        searched_board.status = new_status

        if new_tag_names:
            searched_board.tags = []
            for tag_name in new_tag_names:
                tag_name = tag_name.strip().lower()
                if not tag_name:
                    continue
                found_tag = Tag.query.filter_by(name=tag_name).first()
                if not found_tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                    searched_board.tags.append(tag)
                else:
                    searched_board.tags.append(found_tag)

        if new_member_ids:
            found_members = User.query.filter(User.id.in_(new_member_ids)).all()
            owner = User.query.get(user_id)
            if owner and owner not in found_members:
                found_members.append(owner)
            searched_board.members = found_members

        db.session.commit()
        return jsonify({"message": f"Tablero con id: {board_id} actualizado correctamente"}), 200

    except Exception as e:
        logger.error(f"Error al actualizar tabla: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error al actualizar la tabla"
        }), 500

def delete_board(board_id):
    user_id = int(get_jwt_identity())
    searched_board = (
        db.session.query(Board)
        .join(UserBoard, UserBoard.board_id == Board.id)
        .filter(UserBoard.user_id == user_id, Board.id == board_id)
        .first()
    )

    if searched_board is None:
        return jsonify({"error": f"El tablero con id: {board_id} no fue encontrado"}), 404

    if searched_board.owner_id != user_id:
        return jsonify({"error": "No tienes permiso para eliminar este tablero"}), 403

    try:
        # 1. Elimina relaciones UserBoard explícitamente
        UserBoard.query.filter_by(board_id=board_id).delete()

        # 2. Elimina el tablero
        db.session.delete(searched_board)
        db.session.commit()

        return jsonify(searched_board.to_dict()), 202

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar el tablero: {str(e)}")
        return jsonify({"error": "Error interno al eliminar el tablero"}), 500



@jwt_required()
def toggle_favorite(board_id):
    try:
        user_id = int(get_jwt_identity())

        user_board = UserBoard.query.filter_by(user_id=user_id, board_id=board_id).first()
        if not user_board:
            return jsonify({"error": "No estás en este tablero"}), 403

        user_board.is_favorite = not user_board.is_favorite
        db.session.commit()

        return jsonify({
            "success": True,
            "is_favorite": user_board.is_favorite
        }), 200

    except Exception as e:
        logger.error(f"Error al actualizar favorito: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error al actualizar favorito"
        }), 500
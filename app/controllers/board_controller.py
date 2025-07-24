from app.models.user import User
from app.models.board import Board
from app.models.tag import Tag
from app.database.database import db
from flask import jsonify ,request
from ..logs.logger import logger

#CRUD FOR BOARD

def create_board():
    data= request.json
    try:
        name = data.get("name", None)
        description = data.get("description")
        owner_id = data.get("ownerId", None)
        status = data.get("status", "PRIVATE").upper()
        board_image_url = data.get("boardImageUrl")
        tag_names = data.get('tags', [])
        member_ids = data.get('members', [])

        if name==None or owner_id==None:
            return jsonify({'error': f"Faltan campos obligatorios 'name' o 'ownerId' " }), 400

        new_board = Board(
            name=name,
            description=description,
            owner_id=owner_id,
            status=status,
            board_image_url=board_image_url
        )
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
    
        for user_id in member_ids:
            user = User.query.get(user_id)
            if user and user.id != owner_id:  
                new_board.members.append(user)
        
        owner = User.query.get(owner_id)
        if owner and owner not in new_board.members:
            new_board.members.append(owner)

        db.session.add(new_board)
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
        
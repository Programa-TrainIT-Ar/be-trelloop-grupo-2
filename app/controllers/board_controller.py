from app.models.user import User
from app.models.board import Board
from app.models.tag import Tag
from app.models.relationships import UserBoard, BoardRoleEnum
from app.database.database import db
from flask import jsonify ,request
from flask_jwt_extended import get_jwt_identity
from ..logs.logger import logger
from ..utils.cloudinary_uploader import upload_image_to_cloudinary
from flask import abort
from flask_jwt_extended import jwt_required
from datetime import datetime

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
        owner_id = user_id #.id if user_id else None
        if not owner_id:
            return jsonify({'error': "Dueño del tablero no encontrado"}), 
    
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

        db.session.add(new_board)
        db.session.commit() # Necesario para obtener el new_board.id

         # 🆕 Añadir al dueño con rol 'OWNER'
        owner_relationship = UserBoard(
            user_id=owner_id,
            board_id=new_board.id,
            role=BoardRoleEnum.OWNER
        )
        db.session.add(owner_relationship)

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


@jwt_required()
def add_member(board_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        new_member_email = data.get("email")
        new_member_role = data.get("role", "member").lower()

        if not new_member_email:
            return jsonify({"error": "El email del nuevo miembro es requerido"}), 400

        # Verificar si el usuario actual es ADMIN o OWNER
        current_user_relationship = UserBoard.query.filter_by(user_id=user_id, board_id=board_id).first()
        if not current_user_relationship or current_user_relationship.role not in [BoardRoleEnum.ADMIN, BoardRoleEnum.OWNER]:
            return jsonify({"error": "No tienes permiso para agregar miembros"}), 403

        # Encontrar el tablero y el nuevo usuario
        board = Board.query.get(board_id)
        if not board:
            return jsonify({"error": "Tablero no encontrado"}), 404

        new_user = User.query.filter_by(email=new_member_email).first()
        if not new_user:
            return jsonify({"error": "Usuario con ese email no encontrado"}), 404
        
        # Verificar si el usuario ya es miembro
        if UserBoard.query.filter_by(user_id=new_user.id, board_id=board_id).first():
            return jsonify({"message": "El usuario ya es miembro de este tablero"}), 409

        # Agregar al nuevo miembro con su rol
        new_relationship = UserBoard(
            user_id=new_user.id,
            board_id=board.id,
            role=BoardRoleEnum(new_member_role)
        )
        db.session.add(new_relationship)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Miembro agregado exitosamente",
            "member": new_user.to_dict_basic(),
            "role": new_member_role
        }), 201

    except ValueError:
        return jsonify({"error": "El rol especificado no es válido"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@jwt_required()
def remove_member(board_id, member_id):
    try:
        current_user_id = int(get_jwt_identity())

        # Verificar si el usuario actual tiene permisos
        current_user_relationship = UserBoard.query.filter_by(user_id=current_user_id, board_id=board_id).first()
        if not current_user_relationship or current_user_relationship.role not in [BoardRoleEnum.ADMIN, BoardRoleEnum.OWNER]:
            return jsonify({"error": "No tienes permiso para eliminar miembros"}), 403

        # No se puede eliminar a uno mismo
        if current_user_id == member_id:
            return jsonify({"error": "No puedes eliminarte a ti mismo del tablero"}), 403

        # Encontrar la relación a eliminar
        member_relationship = UserBoard.query.filter_by(user_id=member_id, board_id=board_id).first()
        if not member_relationship:
            return jsonify({"error": "El usuario no es miembro de este tablero"}), 404

        # Lógica de permisos de eliminación
        if current_user_relationship.role == BoardRoleEnum.ADMIN and member_relationship.role in [BoardRoleEnum.ADMIN, BoardRoleEnum.OWNER]:
            return jsonify({"error": "Un administrador no puede eliminar a otro administrador o al dueño"}), 403
            
        # Verificar que siempre haya un dueño
        if member_relationship.role == BoardRoleEnum.OWNER and len(board.members) > 1:
            return jsonify({"error": "No puedes eliminar al dueño del tablero"}), 403


        db.session.delete(member_relationship)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Miembro eliminado exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@jwt_required()
def update_member_role(board_id, member_id):
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        new_role_str = data.get("role").lower()

        # Verificar si el usuario actual tiene permisos
        current_user_relationship = UserBoard.query.filter_by(user_id=current_user_id, board_id=board_id).first()
        if not current_user_relationship or current_user_relationship.role not in [BoardRoleEnum.ADMIN, BoardRoleEnum.OWNER]:
            return jsonify({"error": "No tienes permiso para cambiar roles"}), 403
        
        # El dueño no puede cambiarse a sí mismo
        if current_user_id == member_id:
             return jsonify({"error": "No puedes cambiar tu propio rol"}), 403

        # Encontrar la relación a modificar
        member_relationship = UserBoard.query.filter_by(user_id=member_id, board_id=board_id).first()
        if not member_relationship:
            return jsonify({"error": "El usuario no es miembro de este tablero"}), 404

        # Lógica de permisos para la actualización
        if current_user_relationship.role == BoardRoleEnum.ADMIN:
            if new_role_str == BoardRoleEnum.ADMIN.value:
                return jsonify({"error": "Un administrador no puede promover a otro miembro a administrador"}), 403
            if member_relationship.role == BoardRoleEnum.OWNER:
                return jsonify({"error": "Un administrador no puede cambiar el rol del dueño"}), 403
        
        # No se puede eliminar al dueño del tablero de esa forma
        if member_relationship.role == BoardRoleEnum.OWNER and new_role_str != BoardRoleEnum.OWNER.value:
            return jsonify({"error": "No puedes degradar al dueño del tablero"}), 403
            

        member_relationship.role = BoardRoleEnum(new_role_str)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Rol de miembro actualizado",
            "new_role": new_role_str
        }), 200

    except ValueError:
        return jsonify({"error": "El rol especificado no es válido"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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

        # 🔹 Marcar "último uso" si el usuario es miembro y la columna existe
        try:
            user_id = int(get_jwt_identity())
            ub = UserBoard.query.filter_by(user_id=user_id, board_id=board_id).first()
            if ub is not None and hasattr(ub, "last_accessed_at"):
                ub.last_accessed_at = datetime.utcnow()
                db.session.commit()
        except Exception as _:
            # No romper si no existe la columna o falla algo menor
            db.session.rollback()

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

        # sort=last_use (default) | created_at
        sort = (request.args.get("sort") or "last_use").strip().lower()

        query = (
            db.session.query(Board)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id)
        )

        # Si existe la columna last_accessed_at en UserBoard, ordena por uso reciente.
        last_access_col = getattr(UserBoard, "last_accessed_at", None)

        if sort == "last_use" and last_access_col is not None:
            # Uso reciente DESC, empates por nombre ASC
            query = query.order_by(last_access_col.desc().nullslast(), Board.name.asc())
        elif sort == "created_at":
            # Fecha de creación DESC, empates por nombre ASC
            query = query.order_by(Board.created_at.desc(), Board.name.asc())
        else:
            # Fallback seguro si no existe last_accessed_at: creación DESC, nombre ASC
            query = query.order_by(Board.created_at.desc(), Board.name.asc())

        boards = query.all()

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
                        "lastName": m.last_name,
                        "avatarUrl": m.avatar_url
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

        found_members = []

        if new_member_ids:
            for identifier in new_member_ids:
                user = None

                # Si es un número, buscamos por ID
                if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                    user = User.query.get(int(identifier))
                
                # Si es un email
                elif isinstance(identifier, str) and "@" in identifier:
                    user = User.query.filter_by(email=identifier.lower()).first()
                
                # Si es un nombre o parte del nombre
                elif isinstance(identifier, str):
                    user = User.query.filter(User.name.ilike(f"%{identifier.strip()}%")).first()

                if user and user not in found_members:
                    found_members.append(user)

        # Agregar al owner siempre
        owner = User.query.get(user_id)
        if owner and owner not in found_members:
            found_members.append(owner)

        if found_members:
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

        return  jsonify({"success": True, "message": "Board eliminado"}), 200

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
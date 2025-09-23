from app.models.board import Board
from app.models.card import Card
from app.models.card_tag import CardTag
from app.models.list import List
from app.models.relationships import UserBoard
from app.models.user import User
from app.database.database import db
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from ..logs.logger import logger
from datetime import datetime, date
from ..websocket.broadcast import (broadcast_card_moved, broadcast_card_updated, broadcast_card_created, broadcast_card_deleted, broadcast_card_reordered)

def create_card(board_id, list_id):
    """
    Crear una nueva tarjeta con los parámetros necesarios:
    - título, descripción, responsables, prioridad, estado, 
    - etiquetas, fecha de creación, fecha de vencimiento, recordatorio
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        title = data.get("title")
        if not title or not title.strip():
            return jsonify({"error": "El campo 'title' es requerido"}), 400
        
        if len(title.strip()) > 255:
            return jsonify({"error": "El título no puede exceder 255 caracteres"}), 400
        
        description = data.get("description", "").strip()
        priority = data.get("priority", "low")
        valid_priorities = ["low", "medium", "high"]
        if priority and priority not in valid_priorities:
            return jsonify({"error": f"Prioridad debe ser: {', '.join(valid_priorities)}"}), 400
        
        status = data.get("status", "pending")
        tag_names = data.get("tags", [])
        assignee_ids = data.get("assignee_ids", [])
        
        

        # Due date
        start_date = None
        start_date_str = data.get("start_date")
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                
            except ValueError:
                return jsonify({"error": "Formato de fecha de inicio inválido. Use YYYY-MM-DD"}), 400
        
        # End date
        end_date = None
        end_date_str = data.get("end_date")
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                if start_date and end_date < start_date:
                    return jsonify({"error": "La fecha de finalización debe ser posterior o igual a la fecha de inicio"}), 400
            except ValueError:
                return jsonify({"error": "Formato de fecha de finalización inválido. Use YYYY-MM-DD"}), 400
        
        # Reminder date
        reminder_message = data.get("reminder_message", "")
        reminder_date = None
        reminder_date_str = data.get("reminder_date")
        
        if reminder_date_str:
            try:
                reminder_date = datetime.strptime(reminder_date_str, "%Y-%m-%d")
                if start_date and reminder_date < start_date:
                    return jsonify({"error": "La fecha de recordatorio no puede ser anterior a la fecha de inicio"}), 400
                if end_date and reminder_date > end_date:
                    return jsonify({"error": "La fecha de recordatorio no puede ser posterior a la fecha de finalización"}), 400
            except ValueError:
                return jsonify({"error": "Formato de fecha de recordatorio inválido. Use YYYY-MM-DD"}), 400

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
        
        # Validar responsables usando búsqueda flexible
        valid_assignees = []
        if assignee_ids:
            for identifier in assignee_ids:
                user = None
                # ID numérico
                if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                    user = User.query.get(int(identifier))
                # Email
                elif isinstance(identifier, str) and "@" in identifier:
                    user = User.query.filter_by(email=identifier.lower()).first()
                # Nombre o parte del nombre
                elif isinstance(identifier, str):
                    user = (
                        db.session.query(User)
                        .join(UserBoard, UserBoard.user_id == User.id)
                        .filter(UserBoard.board_id == board_id)
                        .filter(User.name.ilike(f"%{identifier.strip()}%"))
                        .first()
                    )
                if user and user not in valid_assignees:
                    valid_assignees.append(user)

            if not valid_assignees:
                return jsonify({"error": "No se encontraron responsables válidos"}), 400


        # Calcular posición al final de la lista
        last_card = (
            db.session.query(Card)
            .filter_by(list_id=list_id)
            .order_by(Card.position.desc())
            .first()
        )
        new_position = 0 if not last_card else last_card.position + 1

        # Crear tarjeta solo si los responsables son válidos o no se enviaron responsables
        new_card = Card(
            title=title.strip(),
            description=description,
            list_id=list_id,
            position=new_position,
            start_date=start_date,
            priority=priority,
            status=status,
            end_date=end_date,
            reminder_message=reminder_message,
            reminder_date=reminder_date
        )

        # Asignar responsables válidos
        if valid_assignees:
            new_card.assignees = valid_assignees

        db.session.add(new_card)
        db.session.flush()

        
        
        # Asignar etiquetas
        if tag_names:
            for tag_name in tag_names:
                 # Buscar tag en el board específico
                tag_name = tag_name.strip().lower()
                if not tag_name:
                    continue
                tag = CardTag.query.filter_by(name=tag_name, board_id=board_id).first()


                if not tag:
                    tag = CardTag(name=tag_name, board_id=board_id)
                    db.session.add(tag)
                    db.session.flush()
                
                if tag not in new_card.tags:
                    new_card.tags.append(tag)
        db.session.commit()
        db.session.refresh(new_card)
        
        broadcast_card_created(board_id, new_card.to_dict(), user_id)

        logger.info(f"Tarjeta '{title}' creada en lista {list_id} por usuario {user_id}")
        # logger.info(f"Nueva Tarjeta: {new_card.to_dict()}")
        
        return jsonify({
            "success": True,
            "message": "Tarjeta creada exitosamente",
            "card": new_card.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error al crear tarjeta en lista {list_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

def get_cards_by_list(board_id, list_id):
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
            return jsonify({"error": f"Tablero {board_id} no encontrado"}), 404
        
        # Verificar que la lista existe
        target_list = (
            db.session.query(List)
            .filter_by(id=list_id, board_id=board_id)
            .first()
        )
        
        if not target_list:
            return jsonify({"error": f"Lista {list_id} no encontrada"}), 404
        
        # Obtener tarjetas ordenadas por posición
        cards = (
            db.session.query(Card)
            .filter_by(list_id=list_id)
            .order_by(Card.position.desc())
            .all()
        )
        
        return jsonify({
            "success": True,
            "list_name": target_list.name,
            "cards": [card.to_dict() for card in cards]
        }), 200
        
    except Exception as e:
        logger.error(f"Error al obtener tarjetas de lista {list_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500
    
def get_card_by_id(board_id, list_id, card_id):
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
            return jsonify({"error": f"Tablero {board_id} no encontrado"}), 404
        
        # Verificar que la lista existe
        target_list = (
            db.session.query(List)
            .filter_by(id=list_id, board_id=board_id)
            .first()
        )
        
        if not target_list:
            return jsonify({"error": f"Lista {list_id} no encontrada"}), 404
    
        card = (
            db.session.query(Card)
            .filter_by(id=card_id, list_id=list_id)
            .first()
        )
        if not card:
            return jsonify({"error": f"Tarjeta {card_id} no encontrada en la lista {list_id}"}), 404
        
        return jsonify({
            "success": True,
            "card": card.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener tarjeta {card_id} de la lista {list_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500
    

def update_card(board_id, list_id, card_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Verificar acceso al tablero
        board = (
            db.session.query(Board)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id, Board.id == board_id)
            .first()
        )
        if not board:
            return jsonify({"error": "Tablero no encontrado"}), 404
        
        # Buscar la tarjeta (NOTA: puede estar en cualquier lista del board)
        card = (
            db.session.query(Card)
            .join(List, List.id == Card.list_id)
            .filter(Card.id == card_id, List.board_id == board_id)
            .first()
        )
        if not card:
            return jsonify({"error": "Tarjeta no encontrada en la lista especificada"}), 404
        
        # Variable para detectar si la tarjeta fue movida
        was_moved = False
        was_reordered = False
        old_list_id = card.list_id
        old_position = card.position
        
        # FUNCIONALIDAD DRAG & DROP
        new_list_id = data.get("list_id", card.list_id)
        new_position = data.get("position")

        # validar que la lista destino existe y pertenece al mismo board
        if new_list_id != card.list_id:
            target_list = (
                db.session.query(List)
                .filter_by(id=new_list_id, board_id=board_id)
                .first()
            )
            
            if not target_list:
                return jsonify({
                    "error": f"La lista destino {new_list_id} no existe o no pertenece al tablero {board_id}"
                }), 400
            
        # CASO 1: Mover entre listas diferentes
        if new_list_id != card.list_id:
            was_moved = True
                
            # Determinar posición en lista destino
            if new_position is not None:
                # Validar posición específica
                max_position = (
                    db.session.query(db.func.max(Card.position))
                    .filter_by(list_id=new_list_id)
                    .scalar() or -1
                )

                if new_position < 0 or new_position > max_position + 1:
                    return jsonify({
                        "error": f"Posición inválida. Debe estar entre 0 y {max_position + 1}"
                    }), 400
                    
                target_position = new_position
            else:
                # Colocar al final por defecto
                last_card_in_target = (
                    db.session.query(Card)
                    .filter_by(list_id=new_list_id)
                    .order_by(Card.position.desc())
                    .first()
                )
                target_position = 0 if not last_card_in_target else last_card_in_target.position + 1
                
            # Reorganizar lista origen (cerrar el gap)
            db.session.query(Card).filter(
                Card.list_id == old_list_id,
                Card.position > old_position
            ).update({Card.position: Card.position - 1})

            # Hacer espacio en lista destino (abrir gap)
            db.session.query(Card).filter(
                Card.list_id == new_list_id,
                Card.position >= target_position
            ).update({Card.position: Card.position + 1})
                
            # Actualizar tarjeta
            card.list_id = new_list_id
            card.position = target_position
                
            logger.info(f"Tarjeta {card_id} movida de lista {old_list_id}:{old_position} a lista {new_list_id}:{target_position}")
        
        # CASO 2: Reordenar dentro de la misma lista
        elif new_position is not None and new_position != old_position:
            was_reordered = True

            # Validar posición dentro de la misma lista
            max_position = (
                db.session.query(db.func.max(Card.position))
                .filter_by(list_id=card.list_id)
                .scalar()
            )
            if new_position < 0 or new_position > max_position:
                return jsonify({
                    "error": f"Posición inválida. Debe estar entre 0 y {max_position}"
                }), 400
            
            # ESTRATEGIA DE REORDENAMIENTO
            if new_position < old_position:
                # Mover hacia abajo: decrementar posiciones intermedias
                db.session.query(Card).filter(
                    Card.list_id == card.list_id,
                    Card.position > old_position,
                    Card.position <= new_position
                ).update({Card.position: Card.position - 1})
            else:
                # Mover hacia arriba: incrementar posiciones intermedias
                db.session.query(Card).filter(
                    Card.list_id == card.list_id,
                    Card.position < old_position,
                    Card.position >= new_position
                ).update({Card.position: Card.position + 1})

            # Actualizar posición de la tarjeta
            card.position = new_position

            logger.info(f"Tarjeta {card_id} reordenada en lista {card.list_id} de posición {old_position} a {new_position}")

        if "title" in data:
            if not data["title"].strip():
                return jsonify({"error": "El título no puede estar vacío"}), 400
            card.title = data["title"].strip()
        
        if "description" in data:
            card.description = data["description"].strip()
        
        if "priority" in data:
            valid_priorities = ["low", "medium", "high"]
            if data["priority"] and data["priority"] not in valid_priorities:
                return jsonify({"error": f"Prioridad debe ser: {', '.join(valid_priorities)}"}), 400
            card.priority = data["priority"]
        
        if "status" in data:
            card.status = data["status"]
               
        if "start_date" in data:
            start_date_str = data["start_date"]
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    card.start_date = start_date
                except ValueError:
                    return jsonify({"error": "Formato de fecha de inicio inválido. Use YYYY-MM-DD"}), 400
            else:
                card.start_date = None
        
        if "end_date" in data:
            end_date_str = data["end_date"]
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    if card.start_date and end_date < card.start_date:
                        return jsonify({"error": "La fecha de vencimiento debe ser posterior o igual a la fecha de inicio"}), 400
                    card.end_date = end_date
                except ValueError:
                    return jsonify({"error": "Formato de fecha de vencimiento inválido. Use YYYY-MM-DD"}), 400
            else:
                card.end_date = None
        # Reminder date
        if "reminder_date" in data:
            reminder_date_str = data["reminder_date"]
            if reminder_date_str:
                try:
                    reminder_date = datetime.strptime(reminder_date_str, "%Y-%m-%d")
                    # Validar que sea >= start_date
                    if card.start_date and reminder_date < card.start_date:
                        return jsonify({"error": "La fecha de recordatorio no puede ser anterior a la fecha de inicio"}), 400
                    # Validar que sea <= end_date
                    if card.end_date and reminder_date > card.end_date:
                        return jsonify({"error": "La fecha de recordatorio no puede ser posterior a la fecha de finalización"}), 400
                    card.reminder_date = reminder_date
                except ValueError:
                    return jsonify({"error": "Formato de fecha de recordatorio inválido. Use YYYY-MM-DD"}), 400
            else:
                card.reminder_date = None
                
        if "reminder_message" in data:
            card.reminder_message = data["reminder_message"]

        # Validar y asignar responsables usando búsqueda flexible
        if "assignee_ids" in data:
            identifiers = data["assignee_ids"]  # lista de ID, email o nombres
            found_members = []

            if identifiers:
                for identifier in identifiers:
                    user = None

                    # ID numérico
                    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                        user = User.query.get(int(identifier))

                    # Email
                    elif isinstance(identifier, str) and "@" in identifier:
                        user = User.query.filter_by(email=identifier.lower()).first()

                    # Nombre o parte del nombre
                    elif isinstance(identifier, str):
                        user = (
                            db.session.query(User)
                            .join(UserBoard, UserBoard.user_id == User.id)
                            .filter(UserBoard.board_id == board_id)
                            .filter(User.name.ilike(f"%{identifier.strip()}%"))
                            .first()
                        )

                    if user and user not in found_members:
                        found_members.append(user)

                if not found_members:
                    return jsonify({"error": "No se encontraron responsables válidos"}), 400

            card.assignees = found_members
        
        # Actualizar tags como lista de nombres
        if "tags" in data:
            new_tag_names = data["tags"]  # lista de strings
            card.tags = []  # Limpiar tags actuales
            if new_tag_names:
                for tag_name in new_tag_names:
                    tag_name = tag_name.strip().lower()
                    if not tag_name:
                        continue

                    # Buscar tag en el board
                    tag = CardTag.query.filter_by(name=tag_name, board_id=board_id).first()
                    if not tag:
                        tag = CardTag(name=tag_name, board_id=board_id)
                        db.session.add(tag)
                        db.session.flush()  # para obtener ID

                    if tag not in card.tags:
                        card.tags.append(tag)

        db.session.commit()
        db.session.refresh(card)

        if was_moved:
            broadcast_card_moved(board_id, card.to_dict(), user_id)
        elif was_reordered:
            broadcast_card_reordered(board_id, card.to_dict(), user_id)
        else:
            broadcast_card_updated(board_id, card.to_dict(), user_id)

        return jsonify({
            "success": True,
            "message": "Tarjeta actualizada exitosamente",
            "card": card.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error al actualizar tarjeta {card_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": "Error interno del servidor"
        }), 500

def delete_card(board_id, list_id, card_id):
    try:
        user_id = int(get_jwt_identity())
        
        # Verificar acceso
        board = (
            db.session.query(Board)
            .join(UserBoard, UserBoard.board_id == Board.id)
            .filter(UserBoard.user_id == user_id, Board.id == board_id)
            .first()
        )
        
        if not board:
            return jsonify({"error": "Tablero no encontrado"}), 404
        
        # Buscar la tarjeta
        card = (
            db.session.query(Card)
            .join(List, List.id == Card.list_id)
            .filter(Card.id == card_id, Card.list_id == list_id,List.board_id == board_id)
            .first()
        )
        
        if not card:
            return jsonify({"error": "Tarjeta no encontrada en la lista especificada"}), 404
        
        position = card.position

        # Eliminar la tarjeta
        db.session.delete(card)

        # Reordenar posiciones de tarjetas restantes
        remaining_cards = (
            db.session.query(Card)
            .filter(Card.list_id == list_id, Card.position > position)
            .all()
        )
        
        for remaining_card in remaining_cards:
            remaining_card.position -= 1

        db.session.commit()

        broadcast_card_deleted(board_id, card_id, user_id)
        
        logger.info(f"Tarjeta {card_id} eliminada por usuario {user_id}")
        
        return '', 204
        
    except Exception as e:
        logger.error(f"Error al eliminar tarjeta {card_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": "Error interno del servidor"
        }), 500
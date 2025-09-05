from app.models.board import Board
from app.models.card import Card
from app.models.card_tag import CardTag
from app.models.list import List
from app.models.relationships import UserBoard
from app.models.user import User
from app.database.database import db
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from ..logs.logger import logger
from datetime import datetime, date

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
        
        # Validación de fechas
        today = datetime.utcnow().date()

        # Due date
        start_date = None
        start_date_str = data.get("start_date")
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                if start_date.date() < today:
                    return jsonify({"error": "La fecha de inicio no puede ser anterior a hoy"}), 400
            except ValueError:
                return jsonify({"error": "Formato de fecha de inicio inválido. Use YYYY-MM-DD"}), 400
        
        # End date
        end_date = None
        end_date_str = data.get("end_date")
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                if end_date.date() < today:
                    return jsonify({"error": "La fecha de finalizacion no puede ser anterior a hoy"}), 400
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
        
        logger.info(f"Tarjeta '{title}' creada en lista {list_id} por usuario {user_id}")
        logger.info(f"Nueva Tarjeta: {new_card.to_dict()}")
        
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
        
        # Buscar la tarjeta
        card = (
            db.session.query(Card)
            .join(List, List.id == Card.list_id)
            .filter(Card.id == card_id, Card.list_id == list_id, List.board_id == board_id)
            .first()
        )
        if not card:
            return jsonify({"error": "Tarjeta no encontrada en la lista especificada"}), 404
        
        # Actualizar campos básicos
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
        
        # Validación de fechas
        today = datetime.utcnow().date()
        
        if "start_date" in data:
            start_date_str = data["start_date"]
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    if start_date.date() < today:
                        return jsonify({"error": "La fecha de inicio no puede ser anterior a hoy"}), 400
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
                    if end_date.date() < today:
                        return jsonify({"error": "La fecha de vencimiento no puede ser anterior a hoy"}), 400
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
        
        logger.info(f"Tarjeta {card_id} eliminada por usuario {user_id}")
        
        return '', 204
        
    except Exception as e:
        logger.error(f"Error al eliminar tarjeta {card_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": "Error interno del servidor"
        }), 500
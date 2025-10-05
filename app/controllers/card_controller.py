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
from ..services.notification_service import notification_service

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

        # Crear notificaciones para los responsables asignados
        if valid_assignees:
            assigned_by_user = User.query.get(user_id)
            for assignee in valid_assignees:
                notification_service.create_assignment_notification(
                    user=assignee,
                    card=new_card,
                    assigned_by_user=assigned_by_user
                )
        
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

        # Buscar la tarjeta
        card = (
            db.session.query(Card)
            .join(List, List.id == Card.list_id)
            .filter(Card.id == card_id, List.board_id == board_id)
            .first()
        )
        if not card:
            return jsonify({"error": "Tarjeta no encontrada en la lista"}), 404

        old_list_id = card.list_id
        old_position = card.position

        # Guardar responsables actuales para comparar cambios (puede ser vacío)
        old_assignees = set(assignee.id for assignee in card.assignees) if card.assignees else set()

        # FUNCIONALIDAD DRAG & DROP
        new_list_id = data.get("list_id", old_list_id)
        new_position = data.get("position", old_position)

        # Normalizar new_position a int cuando venga como string (seguro y no rompedor)
        try:
            if new_position is None:
                new_position = old_position
            elif isinstance(new_position, str):
                new_position = int(new_position)
            else:
                # si viene float/otro, intentamos convertir a int
                new_position = int(new_position)
        except Exception:
            new_position = old_position

        was_moved = new_list_id != old_list_id
        was_reordered = (not was_moved) and (new_position != old_position)

        # Validar lista destino si se mueve
        if was_moved:
            target_list = db.session.query(List).filter_by(id=new_list_id, board_id=board_id).first()
            if not target_list:
                return jsonify({"error": "Lista destino inválida"}), 400

        # ----- OBTENER TODAS LAS TARJETAS ORDENADAS -----
        source_cards = db.session.query(Card).filter_by(list_id=old_list_id).order_by(Card.position).all()
        target_cards = (
            db.session.query(Card).filter_by(list_id=new_list_id).order_by(Card.position).all()
            if was_moved
            else source_cards
        )

        # ----- REORDENAMIENTO -----
        if was_moved:
            # Quitar tarjeta de la lista origen
            if card in source_cards:
                source_cards.remove(card)
            for idx, c in enumerate(source_cards):
                c.position = idx

            # Insertar tarjeta en la lista destino
            if new_position < 0:
                new_position = 0
            elif new_position > len(target_cards):
                new_position = len(target_cards)

            target_cards.insert(new_position, card)
            for idx, c in enumerate(target_cards):
                c.position = idx

            card.list_id = new_list_id

        elif was_reordered:
            # Reordenamiento dentro de la misma lista
            if new_position < 0:
                new_position = 0
            elif new_position >= len(source_cards):
                new_position = len(source_cards) - 1

            if card in source_cards:
                source_cards.remove(card)
            source_cards.insert(new_position, card)
            for idx, c in enumerate(source_cards):
                c.position = idx

        # ----- ACTUALIZACIÓN DE CAMPOS -----
        for field in [
            "title",
            "description",
            "priority",
            "status",
            "start_date",
            "end_date",
            "reminder_date",
            "reminder_message",
        ]:
            if field in data:
                value = data[field]
                if field in ["start_date", "end_date", "reminder_date"] and value:
                    try:
                        setattr(card, field, datetime.strptime(value, "%Y-%m-%d"))
                    except ValueError:
                        return jsonify({"error": f"Formato de {field} inválido. Use YYYY-MM-DD"}), 400
                else:
                    setattr(card, field, value)

        # ----- ASIGNADOS -----
        if "assignee_ids" in data:
            found_members = []
            for identifier in data["assignee_ids"]:
                user = None
                if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                    user = User.query.get(int(identifier))
                elif isinstance(identifier, str) and "@" in identifier:
                    user = User.query.filter_by(email=identifier.lower()).first()
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

            # Asignar los encontrados (puede quedar vacío si así se requiere)
            card.assignees = found_members

            # Determinar nuevos responsables asignados para notificaciones
            new_assignees = set(member.id for member in found_members) if found_members else set()
            newly_assigned = new_assignees - old_assignees

            # Crear notificaciones sólo para nuevos responsables
            if newly_assigned:
                assigned_by_user = User.query.get(user_id)
                for assignee_id in newly_assigned:
                    assignee = User.query.get(assignee_id)
                    if assignee:
                        # Verificar que no exista ya una notificación
                        existing_notification = notification_service.check_existing_notification(
                            assignee_id, card_id
                        )

                        if not existing_notification:
                            notification_service.create_assignment_notification(
                                user=assignee,
                                card=card,
                                assigned_by_user=assigned_by_user,
                            )
                            logger.info(f"Notificación enviada a nuevo responsable {assignee_id} para tarjeta {card_id}")

        # ----- TAGS -----
        if "tags" in data:
            card.tags = []
            for tag_name in data["tags"]:
                tag_name = tag_name.strip().lower()
                if not tag_name:
                    continue
                tag = CardTag.query.filter_by(name=tag_name, board_id=board_id).first()
                if not tag:
                    tag = CardTag(name=tag_name, board_id=board_id)
                    db.session.add(tag)
                    db.session.flush()
                card.tags.append(tag)

        db.session.commit()
        db.session.refresh(card)

        # ----- BROADCAST -----
        if was_moved:
            broadcast_card_moved(board_id, card.to_dict(), user_id)
        elif was_reordered:
            broadcast_card_reordered(board_id, card.to_dict(), user_id)
        else:
            broadcast_card_updated(board_id, card.to_dict(), user_id)

        return (
            jsonify({"success": True, "message": "Tarjeta actualizada exitosamente", "card": card.to_dict()}),
            200,
        )

    except Exception as e:
        logger.error(f"Error al actualizar tarjeta {card_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

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
from app.models.board import Board
from app.models.card import Card, CardAssignee, Tag
from app.models.list import List
from app.models.relationships import UserBoard
from app.models.user import User
from app.database.database import db
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from ..logs.logger import logger

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
        
        assignee_ids = data.get("assignees", [])
    
        priority = data.get("priority")
        valid_priorities = ["low", "medium", "high"]
        if priority and priority not in valid_priorities:
            return jsonify({"error": f"Prioridad debe ser: {', '.join(valid_priorities)}"}), 400
        
        status = data.get("status", "pending")
        tag_ids = data.get("tags", [])
        
        due_date = None
        due_date_str = data.get("due_date")
        if due_date_str:
            try:
                # Formato: "2025-08-20" o "2025-08-20T18:00:00"
                for date_format in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        due_date = datetime.strptime(due_date_str, date_format)
                        break
                    except ValueError:
                        continue
                
                if due_date is None:
                    return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS"}), 400
            except Exception:
                return jsonify({"error": "Error al procesar la fecha de vencimiento"}), 400
        
        reminder_date = None
        reminder_message = data.get("reminder_message", "")
        reminder_date_str = data.get("reminder_date")
        if reminder_date_str:
            try:
                for date_format in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        reminder_date = datetime.strptime(reminder_date_str, date_format)
                        break
                    except ValueError:
                        continue
                
                if reminder_date is None:
                    return jsonify({"error": "Formato de fecha de recordatorio inválido"}), 400
            except Exception:
                return jsonify({"error": "Error al procesar la fecha del recordatorio"}), 400
        
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
        
        # Calcular posición (al final de la lista)
        last_card = (
            db.session.query(Card)
            .filter_by(list_id=list_id)
            .order_by(Card.position.desc())
            .first()
        )
        
        new_position = 0 if not last_card else last_card.position + 1
        
        # Crear la tarjeta
        new_card = Card(
            title=title.strip(),
            description=description,
            list_id=list_id,
            position=new_position,
            due_date=due_date,
            priority=priority,
            status=status,
            reminder_date=reminder_date,
            reminder_message=reminder_message
        )
        
        db.session.add(new_card)
        db.session.flush()  # Para obtener el ID
        
        # Asignar responsables
        if assignee_ids:
            # Validar que los usuarios tienen acceso al tablero
            valid_assignees = (
                db.session.query(User)
                .join(UserBoard, UserBoard.user_id == User.id)
                .filter(User.id.in_(assignee_ids), UserBoard.board_id == board_id)
                .all()
            )
            
            if len(valid_assignees) != len(assignee_ids):
                return jsonify({"error": "Algunos responsables no tienen acceso al tablero"}), 400
            
            # Crear las asignaciones
            for user in valid_assignees:
                card_assignee = CardAssignee(card_id=new_card.id, user_id=user.id)
                db.session.add(card_assignee)
        
        # Asignar etiquetas
        if tag_ids:
            # Validar que las etiquetas pertenecen al tablero
            valid_tags = (
                db.session.query(Tag)
                .filter(Tag.id.in_(tag_ids), Tag.board_id == board_id)
                .all()
            )
            
            if len(valid_tags) != len(tag_ids):
                return jsonify({"error": "Algunas etiquetas no pertenecen al tablero"}), 400
            
            # Asignar las etiquetas
            new_card.tags = valid_tags
        
        db.session.commit()
        
        created_card = db.session.query(Card).filter_by(id=new_card.id).first()
        
        logger.info(f"Tarjeta '{title}' creada en lista {list_id} por usuario {user_id}")
        
        return jsonify({
            "success": True,
            "message": "Tarjeta creada exitosamente",
            "card": created_card.to_dict()
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
            .order_by(Card.position)
            .all()
        )
        
        return jsonify({
            "success": True,
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
        
        # Actualizar campos
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
        
        # Actualizar fecha de vencimiento
        if "due_date" in data:
            if data["due_date"]:
                try:
                    card.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
                except ValueError:
                    return jsonify({"error": "Formato de fecha inválido"}), 400
            else:
                card.due_date = None
        
        # Actualizar recordatorio
        if "reminder_date" in data:
            if data["reminder_date"]:
                try:
                    card.reminder_date = datetime.strptime(data["reminder_date"], "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    return jsonify({"error": "Formato de fecha de recordatorio inválido"}), 400
            else:
                card.reminder_date = None
        
        if "reminder_message" in data:
            card.reminder_message = data["reminder_message"]
        
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
        
        # Eliminar la tarjeta
        db.session.delete(card)
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
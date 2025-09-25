from app.models.notification import Notification, StatusNotificationEnum, NotificationPriorityEnum
from app.database.database import db
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from ..logs.logger import logger


def get_notifications():
    """
    Obtener todas las notificaciones del usuario autenticado.
    """
    try:
        user_id = int(get_jwt_identity())

        # Obtener notificaciones del usuario, ordenadas por fecha
        notifications = (
            db.session.query(Notification)
            .filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

        return jsonify({
            "success": True,
            "notifications": [n.to_dict() for n in notifications]
        }), 200

    except Exception as e:
        logger.error(f"Error al obtener notificaciones del usuario {user_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

def mark_notification_as_read(notification_id):
    """
    Marcar una notificación como leída (status: READ).
    """
    try:
        user_id = int(get_jwt_identity())

        # Buscar la notificación que pertenezca al usuario
        notification = (
            db.session.query(Notification)
            .filter_by(id=notification_id, user_id=user_id)
            .first()
        )

        if not notification:
            return jsonify({"error": f"Notificación {notification_id} no encontrada"}), 404

        # Cambiar estado solo si está UNREAD
        if notification.status == StatusNotificationEnum.UNREAD:
            notification.status = StatusNotificationEnum.READ
            db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Notificación {notification_id} marcada como leída",
            "notification": notification.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error al marcar notificación {notification_id} como leída: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


def test_create_notification():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    description = data.get("description", "Notificación de prueba")

    notification = Notification(
        user_id=user_id,
        card_id=data.get("card_id", 1),  # usar una tarjeta de prueba
        description=description,
        status=StatusNotificationEnum.UNREAD,
        priority=NotificationPriorityEnum.LOW
    )

    db.session.add(notification)
    db.session.commit()
    return jsonify({"success": True, "notification": notification.to_dict()}), 201

from flask import current_app
from flask_socketio import emit
from datetime import datetime
from ..logs.logger import logger

def get_socketio():
    if hasattr(current_app, 'extensions') and 'socketio' in current_app.extensions:
        return current_app.extensions['socketio']
    return None

def broadcast_card_moved(board_id, card_data, moved_by_user_id):
    """
    Notificación en tiempo real cuando una tarjeta es movida
    """
    try:
        socketio = get_socketio()
        if not socketio:
            logger.warning("SocketIO no está disponible para broadcast")
            return
            
        room_name = f'board_{board_id}'
        
        event_data = {
            'type': 'card_moved',
            'board_id': board_id,
            'card': card_data,
            'moved_by': moved_by_user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Emitir a todos los usuarios en el room del board
        socketio.emit(
            'card_updated', 
            event_data, 
            room=room_name
        )
        
        logger.info(f"Broadcast enviado al room {room_name}: tarjeta {card_data.get('id')} movida")
        
    except Exception as e:
        logger.error(f"Error en broadcast_card_moved: {str(e)}")

def broadcast_card_updated(board_id, card_data, updated_by_user_id):
    """
    Envía notificación cuando una tarjeta es actualizada (sin mover)
    """
    try:
        socketio = get_socketio()
        if not socketio:
            logger.warning("SocketIO no está disponible para broadcast")
            return
            
        room_name = f'board_{board_id}'
        
        event_data = {
            'type': 'card_updated',
            'board_id': board_id,
            'card': card_data,
            'updated_by': updated_by_user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit(
            'card_updated', 
            event_data, 
            room=room_name
        )
        
        logger.info(f"Broadcast enviado al room {room_name}: tarjeta {card_data.get('id')} actualizada")
        
    except Exception as e:
        logger.error(f"Error en broadcast_card_updated: {str(e)}")

def broadcast_card_created(board_id, card_data, created_by_user_id):
    """
    Envía notificación cuando una nueva tarjeta es creada
    """
    try:
        socketio = get_socketio()
        if not socketio:
            logger.warning("SocketIO no está disponible para broadcast")
            return
            
        room_name = f'board_{board_id}'
        
        event_data = {
            'type': 'card_created',
            'board_id': board_id,
            'card': card_data,
            'created_by': created_by_user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit(
            'card_updated', 
            event_data, 
            room=room_name
        )
        
        logger.info(f"Broadcast enviado al room {room_name}: nueva tarjeta {card_data.get('id')} creada")
        
    except Exception as e:
        logger.error(f"Error en broadcast_card_created: {str(e)}")

def broadcast_card_deleted(board_id, card_id, deleted_by_user_id):
    """
    Envía notificación cuando una tarjeta es eliminada
    """
    try:
        socketio = get_socketio()
        if not socketio:
            logger.warning("SocketIO no está disponible para broadcast")
            return
            
        room_name = f'board_{board_id}'
        
        event_data = {
            'type': 'card_deleted',
            'board_id': board_id,
            'card_id': card_id,
            'deleted_by': deleted_by_user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit(
            'card_updated', 
            event_data, 
            room=room_name
        )
        
        logger.info(f"Broadcast enviado al room {room_name}: tarjeta {card_id} eliminada")
        
    except Exception as e:
        logger.error(f"Error en broadcast_card_deleted: {str(e)}")
from flask import session
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from app.models.board import Board
from app.models.relationships import UserBoard
from app.database.database import db
from datetime import datetime
from ..logs.logger import logger

def register_board_events(socketio):
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Maneja la conexión inicial del cliente"""
        try:
            # Verificar token JWT
            if not auth or 'token' not in auth:
                logger.warning("Conexión WebSocket sin token JWT")
                disconnect()
                return False
            
            token = auth['token']
            try:
                # Decodificar el token (sin Bearer)
                if token.startswith('Bearer '):
                    token = token[7:]
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
            except Exception as e:
                logger.error(f"Token JWT inválido en WebSocket: {str(e)}")
                disconnect()
                return False
            
            # Almacenar user_id en la sesión
            session['user_id'] = user_id
            logger.info(f"Usuario {user_id} conectado via WebSocket")
            
        except Exception as e:
            logger.error(f"Error en conexión WebSocket: {str(e)}")
            disconnect()
            return False

    @socketio.on('join_board')
    def handle_join_board(data):
        """Permite al usuario unirse a un room específico del board"""
        try:
            board_id = data.get('board_id')
            user_id = session.get('user_id')
            
            if not board_id or not user_id:
                emit('error', {'message': 'Datos faltantes para unirse al board'})
                return
            
            # Verificar que el usuario tiene acceso al board
            user_board = (
                db.session.query(UserBoard)
                .filter_by(user_id=user_id, board_id=board_id)
                .first()
            )
            
            if not user_board:
                emit('error', {'message': 'No tienes acceso a este tablero'})
                return
            
            # Unirse al room del board
            room_name = f'board_{board_id}'
            join_room(room_name)
            
            logger.info(f"Usuario {user_id} se unió al room {room_name}")
            emit('joined_board', {
                'board_id': board_id,
                'message': 'Conectado al tablero exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error al unirse al board: {str(e)}")
            emit('error', {'message': 'Error interno del servidor'})

    @socketio.on('leave_board')
    def handle_leave_board(data):
        """Permite al usuario salir de un room del board"""
        try:
            board_id = data.get('board_id')
            user_id = session.get('user_id')
            
            if board_id and user_id:
                room_name = f'board_{board_id}'
                leave_room(room_name)
                logger.info(f"Usuario {user_id} salió del room {room_name}")
                
        except Exception as e:
            logger.error(f"Error al salir del board: {str(e)}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Maneja la desconexión del cliente"""
        user_id = session.get('user_id')
        if user_id:
            logger.info(f"Usuario {user_id} desconectado de WebSocket")
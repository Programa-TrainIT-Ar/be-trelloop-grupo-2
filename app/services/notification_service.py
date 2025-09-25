import pusher
import resend
from ..config.config import config
from ..models.notification import Notification
from ..database.database import db
from ..logs.logger import logger
from datetime import datetime

class NotificationService:
    def __init__(self):
        # Inicializar Pusher
        self.pusher_client = pusher.Pusher(
            app_id=config["PUSHER_APP_ID"],
            key=config["PUSHER_KEY"], 
            secret=config["PUSHER_SECRET"],
            cluster=config["PUSHER_CLUSTER"],
            ssl=True
        )
        
        # Inicializar Resend
        resend.api_key = config["RESEND_API_KEY"]
        
    def create_assignment_notification(self, user, card, assigned_by_user):
        """
        Crear notificación cuando se asigna un responsable a una tarjeta
        """
        try:
            # Mapear prioridad de la tarjeta
            priority_map = {
                'low': 'baja',
                'medium': 'media', 
                'high': 'alta'
            }
            
            # Crear registro en BD
            notification = Notification(
                user_id=user.id,
                card_id=card.id,
                titulo_tarjeta=card.title,
                descripcion=f"Te han asignado como responsable de la tarjeta '{card.title}' por {assigned_by_user.name} {assigned_by_user.last_name}",
                estado='no_leida',
                prioridad=priority_map.get(card.priority, 'media')
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Enviar notificación en tiempo real via Pusher
            self._send_pusher_notification(user.id, notification)
            
            # Enviar email via Resend
            self._send_email_notification(user, card, assigned_by_user, notification)
            
            logger.info(f"Notificación creada para usuario {user.id} - tarjeta {card.id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creando notificación: {str(e)}")
            db.session.rollback()
            return None
    
    def _send_pusher_notification(self, user_id, notification):
        """
        Enviar notificación en tiempo real via Pusher
        """
        try:
            channel_name = f'user-{user_id}'
            event_data = {
                'id': notification.id,
                'title': 'Nueva tarea asignada',
                'message': notification.descripcion,
                'card_id': notification.card_id,
                'card_title': notification.titulo_tarjeta,
                'priority': notification.prioridad,
                'timestamp': notification.fecha_creacion.isoformat(),
                'type': 'task_assignment'
            }
            
            self.pusher_client.trigger(channel_name, 'new-notification', event_data)
            logger.info(f"Notificación Pusher enviada al canal {channel_name}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación Pusher: {str(e)}")
    
    def _send_email_notification(self, user, card, assigned_by_user, notification):
        """
        Enviar email via Resend.com
        """
        try:
            # Crear URL para ir a la tarjeta específica
            card_url = f"{config['FRONTEND_URL']}/boards/{card.list.board_id}/cards/{card.id}"
            
            # Mapear prioridad para mostrar
            priority_display = {
                'baja': 'Baja',
                'media': 'Media',
                'alta': 'Alta'
            }
            
            # HTML del email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #0079bf; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f8f9fa; }}
                    .card-info {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                    .priority-alta {{ color: #bf2600; font-weight: bold; }}
                    .priority-media {{ color: #ff8b00; font-weight: bold; }}
                    .priority-baja {{ color: #006644; font-weight: bold; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #0079bf; color: white; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Nueva Tarea Asignada</h1>
                    </div>
                    <div class="content">
                        <p>Hola {user.name},</p>
                        <p><strong>{assigned_by_user.name} {assigned_by_user.last_name}</strong> te ha asignado una nueva tarea:</p>
                        
                        <div class="card-info">
                            <h3>{card.title}</h3>
                            <p><strong>Descripción:</strong> {card.description or 'Sin descripción'}</p>
                            <p><strong>Prioridad:</strong> <span class="priority-{notification.prioridad}">{priority_display[notification.prioridad]}</span></p>
                            <p><strong>Lista:</strong> {card.list.name if card.list else 'Sin lista'}</p>
                            {f'<p><strong>Fecha de inicio:</strong> {card.start_date.strftime("%d/%m/%Y") if card.start_date else "No definida"}</p>' if card.start_date else ''}
                            {f'<p><strong>Fecha límite:</strong> {card.end_date.strftime("%d/%m/%Y") if card.end_date else "No definida"}</p>' if card.end_date else ''}
                        </div>
                        
                        <a href="{card_url}" class="button">Ver Tarea</a>
                        
                        <p>Puedes revisar todos los detalles y comenzar a trabajar en la tarea haciendo clic en el botón de arriba.</p>
                    </div>
                    <div class="footer">
                        <p>Este email fue enviado automáticamente por el sistema de gestión de tareas.</p>
                        <p>Si tienes preguntas, contacta con {assigned_by_user.name} ({assigned_by_user.email})</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Enviar email
            resend.Emails.send({
                "from": config["RESEND_FROM_EMAIL"],
                "to": [user.email],
                "subject": "Nueva tarea asignada",
                "html": html_content,
                "reply_to": assigned_by_user.email
            })
            
            logger.info(f"Email enviado a {user.email} para tarjeta {card.id}")
            
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
    
    def check_existing_notification(self, user_id, card_id):
        """
        Verificar si ya existe una notificación para este usuario y tarjeta
        """
        return Notification.query.filter_by(
            user_id=user_id, 
            card_id=card_id
        ).first()
    
    def mark_as_read(self, notification_id, user_id):
        """
        Marcar notificación como leída
        """
        try:
            notification = Notification.query.filter_by(
                id=notification_id, 
                user_id=user_id
            ).first()
            
            if notification:
                notification.estado = 'leida'
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error marcando notificación como leída: {str(e)}")
            db.session.rollback()
            return False

# Instancia global del servicio
notification_service = NotificationService()
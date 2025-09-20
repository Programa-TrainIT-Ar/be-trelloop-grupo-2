from ..database.database import db
import enum
from datetime import datetime
from sqlalchemy import Enum as SQLEnum


class NotificationPriorityEnum(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class StatusNotificationEnum(enum.Enum):
    READ = "read"
    UNREAD = "unread"


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id', ondelete='CASCADE'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(SQLEnum(StatusNotificationEnum, name = 'status', create_type=True), nullable=False, default=StatusNotificationEnum.UNREAD)
    priority = db.Column(SQLEnum(NotificationPriorityEnum, name = 'priority', create_type=True), nullable=False, default=NotificationPriorityEnum.LOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates='notifications')
    card = db.relationship("Card", back_populates='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            
        }
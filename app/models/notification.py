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
    card_title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(SQLEnum(StatusNotificationEnum, name = 'status', create_type=True), nullable=False, default=StatusNotificationEnum.UNREAD)
    priority = db.Column(SQLEnum(NotificationPriorityEnum, name = 'priority', create_type=True), nullable=False, default=NotificationPriorityEnum.LOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates='notifications')
    card = db.relationship("Card", back_populates='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'card_id': self.card_id,
            'card_title': self.card_title,
            'description': self.description,
            'status': self.status.value if isinstance(self.status, enum.Enum) else self.status,
            'priority': self.priority.value if isinstance(self.priority, enum.Enum) else self.priority,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict_basic() if self.user else None,
            'card': {
                'id': self.card.id,
                'title': self.card.title,
                'list_name': self.card.list.name if self.card.list else None
            } if self.card else None
        }
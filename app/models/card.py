from ..database.database import db
from datetime import datetime
from .relationships import card_tags_assoc

class Card(db.Model):
    """Card model for individual tasks within lists"""
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True) 
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), nullable=True, default='low')  # 'low', 'medium', 'high'
    status = db.Column(db.String(20), default='pending')
    reminder_date = db.Column(db.DateTime, nullable=True)
    reminder_message = db.Column(db.String(255), nullable=True)

    list = db.relationship('List', back_populates='cards')
    
    # Many-to-many relationship with users
    assignees = db.relationship(
        'User',
        secondary='card_assignees',
        backref='assigned_cards'
    )

    # Many-to-many relationship with tags
    tags = db.relationship(
        'CardTag',
        secondary=card_tags_assoc,
        backref='cards'
    )

    def to_dict(self):
        """Convert card to dictionary for API responses"""
        # Mapear prioridades para el frontend
        priority_map = {
            'low': 'Baja',
            'medium': 'Media',
            'high': 'Alta'
        }

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'list_id': self.list_id,
            'position': self.position,
            'created_at': self.created_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': priority_map.get(self.priority, self.priority),
            'status': self.list.name if self.list else self.status,
            'reminder_date': self.reminder_date.isoformat() if self.reminder_date else None,
            'reminder_message': self.reminder_message,
            'assignees': [user.to_dict_basic() for user in self.assignees] if self.assignees else [],
            'tags': [
                {
                    'id': tag.id,
                    'name': tag.name
                } for tag in self.tags
            ] if self.tags else []
        }


class CardComment(db.Model):
    """Card comment model for user comments on cards"""
    tablename = 'card_comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert comment to dictionary for API responses"""
        return {
            'id': self.id,
            'card_id': self.card_id,
            'user_id': self.user_id,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

class CardAssignee(db.Model):
    """Card assignee model for many-to-many relationship between users and cards"""
    __tablename__ = 'card_assignees'
    
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
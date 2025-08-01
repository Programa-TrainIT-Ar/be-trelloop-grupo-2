from ..database.database import db
from datetime import datetime

class Card(db.Model):
    """Card model for individual tasks within lists"""
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True) 
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    list = db.relationship('List', back_populates='cards')
    
    def to_dict(self):
        """Convert card to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'list_id': self.list_id,
            'position': self.position,
            'created_at': self.created_at.isoformat()
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
    tablename = 'card_assignees'
    
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
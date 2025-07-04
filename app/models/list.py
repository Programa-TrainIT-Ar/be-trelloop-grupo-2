from ..database import db
from datetime import datetime

class List(db.Model):
    """List model for organizing cards within boards"""
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cards = db.relationship('Card', backref='list', lazy=True, order_by='Card.position')
    
    def to_dict(self):
        """Convert list to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'board_id': self.board_id,
            'position': self.position,
            'created_at': self.created_at.isoformat()
        } 
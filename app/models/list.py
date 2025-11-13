from ..database.database import db
from datetime import datetime
from .card import Card

class List(db.Model):
    """List model for organizing cards within boards"""
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False)
    
    board = db.relationship('Board', back_populates='lists')
    cards = db.relationship(
        'Card',
        back_populates='list',
        cascade='all, delete-orphan',
        lazy=True,
        order_by=lambda: db.desc(Card.position),
        passive_deletes=True
    )
    
    def to_dict(self):
        """Convert list to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'created_at': self.created_at.isoformat(),
            'board_id': self.board_id,
            'cards': [card.to_dict() for card in self.cards]
        }
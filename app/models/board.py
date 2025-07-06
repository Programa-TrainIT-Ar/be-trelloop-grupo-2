from ..database.database import db
from datetime import datetime

class Board(db.Model):
    """Board model for project management"""
    __tablename__ = 'boards'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lists = db.relationship('List', backref='board', lazy=True, order_by='List.position')
    members = db.relationship('BoardMember', backref='board', lazy=True)
    
    def to_dict(self):
        """Convert board to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat()
        }

class BoardMember(db.Model):
    """Board member model for many-to-many relationship between users and boards"""
    __tablename__ = 'board_members'
    
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) 
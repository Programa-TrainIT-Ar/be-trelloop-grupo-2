from ..database.database import db
from .relationships import board_tag

class Tag(db.Model):
    """Tag model for labeling boards"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    boards = db.relationship('Board', secondary=board_tag, back_populates='tags')

    def to_dict(self):
        """Convert list to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name
        } 
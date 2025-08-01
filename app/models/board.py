from ..database.database import db
from datetime import datetime
import enum
from sqlalchemy import Enum as SQLEnum
from .relationships import board_tag
class BoardStatusEnum(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class Board(db.Model):
    """Board model for project management"""
    __tablename__ = 'boards'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    board_image_url = db.Column(db.String(360), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(SQLEnum(BoardStatusEnum, name='board_status', create_type=True), nullable=False, default=BoardStatusEnum.PRIVATE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('User', secondary='user_board', back_populates="boards")
    tags = db.relationship('Tag', secondary=board_tag, back_populates='boards')
    lists = db.relationship('List', back_populates='board', cascade='all, delete-orphan', lazy=True, order_by='List.position')
    
    def to_dict(self):
        """Convert board to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'status': self.status.value,
            'board_image_url': self.board_image_url,
            'members': [member.to_dict_basic() for member in self.members],
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'lists': [list.to_dict() for list in self.lists]
        }
    
    def to_dict_basic(self):
        return {
            'name': self.name,
            "description": self.description,
            'id': self.id,
        }


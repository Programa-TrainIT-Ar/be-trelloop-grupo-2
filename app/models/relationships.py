from ..database.database import db
import enum
from sqlalchemy import Enum as SQLEnum 

class BoardRoleEnum(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class UserBoard (db.Model):
    __tablename__ = 'user_board'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False) #Nuevo campo para el manejo de favoritos
    role = db.Column(SQLEnum(BoardRoleEnum, name = 'board_role', create_type=True), nullable=False, default=BoardRoleEnum.MEMBER) #Nueva columna para el rol.
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'board_id': self.board_id,
            'is_favorite': self.is_favorite,
            'role': self.role.value
        }


board_tag = db.Table(
    'board_tag',
    db.Column('board_id', db.Integer, db.ForeignKey('boards.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
  
)

card_tags_assoc = db.Table(
    'card_tags_assoc',
    db.Column('card_id', db.Integer, db.ForeignKey('cards.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('card_tags.id'), primary_key=True)
)
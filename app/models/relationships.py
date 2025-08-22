from ..database.database import db

class UserBoard (db.Model):
    __tablename__ = 'user_board'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False) #Nuevo campo para el manejo de favoritos
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'board_id': self.board_id,
            'is_favorite': self.is_favorite
        }


board_tag = db.Table(
    'board_tag',
    db.Column('board_id', db.Integer, db.ForeignKey('boards.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
  
)

card_tag = db.Table(
    'card_tag',
    db.Column('card_id', db.Integer, db.ForeignKey('cards.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('card_tags.id'), primary_key=True)
)
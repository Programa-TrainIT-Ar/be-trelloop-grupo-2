from ..database.database import db

class CardTag(db.Model):
    """Tag model for labeling boards"""
    __tablename__ = 'card_tags'
    

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete="CASCADE"), nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'board_id', name='unique_cardtag_per_board'),)

    def to_dict(self):
        """Convert list to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'board_id': self.board_id
        } 
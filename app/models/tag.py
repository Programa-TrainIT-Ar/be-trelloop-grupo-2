from ..database.database import db

class Tag(db.Model):
    """Tag model for labeling boards"""
    __tablename__ = 'tags'
    

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(20), nullable=False, default="#414141")
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'board_id', name='unique_tag_per_board'),)

    def to_dict(self):
        """Convert list to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'board_id': self.board_id
        } 
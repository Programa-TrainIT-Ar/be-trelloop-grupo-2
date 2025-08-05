from ..database.database import db
from datetime import datetime
import bcrypt

DEFAULT_AVATAR_URL = "https://res.cloudinary.com/djw3lkdam/image/upload/v1754147240/samples/cloudinary-icon.png"

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(360), nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    boards = db.relationship('Board', secondary='user_board', back_populates="members")

    def set_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password = hashed.decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'avatar_url': self.avatar_url or DEFAULT_AVATAR_URL,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'boards': [board.to_dict_basic() for board in self.boards]
        }

    def to_dict_basic(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'avatar_url': self.avatar_url or DEFAULT_AVATAR_URL
        }


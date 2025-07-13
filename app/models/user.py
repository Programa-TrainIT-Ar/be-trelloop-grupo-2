from ..database.database import db
from datetime import datetime
import bcrypt

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Relationships
    boards_owned = db.relationship('Board', backref='owner', lazy=True)
    board_memberships = db.relationship('BoardMember', backref='user', lazy=True)
    card_comments = db.relationship('CardComment', backref='user', lazy=True)
    card_assignments = db.relationship('CardAssignee', backref='user', lazy=True)

    def set_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password = hashed.decode('utf-8')

    def check_password(self, password):
        """Verify password against stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        } 
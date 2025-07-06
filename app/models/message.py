from ..database.database import db

class Message(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     content = db.Column(db.String(255), nullable=False)

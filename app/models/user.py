from ..database.database import db

class User(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(255), nullable=False)
     password = db.Column(db.String(255), nullable=False)
     password2 = db.Column(db.String(255), nullable=False)
     password3 = db.Column(db.String(255), nullable=False)


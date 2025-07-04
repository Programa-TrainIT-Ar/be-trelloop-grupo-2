from .database import db
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)  # Contraseña hasheada
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, nombre, correo, contrasena):
        self.nombre = nombre
        self.correo = correo
        self.contrasena = bcrypt.generate_password_hash(contrasena).decode('utf-8')

    def __repr__(self):
        return f'<User {self.correo}>'
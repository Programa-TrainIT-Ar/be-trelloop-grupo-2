from app.models.user import User
from app.database.database import db
from flask import jsonify ,request
from ..logs.logger import logger
import bcrypt
from flask_jwt_extended import create_access_token

#CRUD FOR USERS
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

def login_users():
    data = request.json
    email = data.get("email", None)
    password = data.get("password", None)
    if email ==None or password==None:
        return jsonify({"message": "Falta el correo o la contraseña"}), 400
    user = User.query.filter_by(email=email).first()

    if user ==None:
        return jsonify({"message": "Usuario no encontrado"}), 404
    password_matching = user.check_password(password)

    if password_matching:
        access_token = create_access_token(identity=email)
        return jsonify({"token": access_token,
                        "user" : user.to_dict()})
    return jsonify({"message": "Usuario o contraseña invalida"}), 401

def protected_users():
    return jsonify({"message": "This is a protected route"})
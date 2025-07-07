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
    user = User.query.filter_by(email=email).first

    if user ==None:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    password_bytes = bytes(password, 'utf-8')   
    password_matching = bcrypt.checkpw(password_bytes, user.password.encode('utf-8'))
    if password_matching:
        access_token = create_access_token(identity=email)
        return jsonify({"token": access_token,
                        "user" : user.to_dict()})
    return jsonify({"message": "Contraseña Invalida"}), 401


def create_users():
    data = request.json
    user = User(
        name = data["name"],
        email = data["email"]
    )
    user.set_password(data["password"])
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"Usuario creado: {user.email}")

    return jsonify({"message": "Usuario creado exitosamente"}), 201
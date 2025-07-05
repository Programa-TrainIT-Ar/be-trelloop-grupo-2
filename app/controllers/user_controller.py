from app.models.user import User
from app.database.database import db
from flask import jsonify ,request
from ..logs.logger import logger

def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

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
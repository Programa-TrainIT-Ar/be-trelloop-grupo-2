from app.models.user import User
from app.database.database import db
from flask import jsonify
from ..logs.logger import logger

def get_users():
    users = User.query.all()
    logger.info("Este es un mensaje de informacion")
    return jsonify({"message": "Soy un usuario"})

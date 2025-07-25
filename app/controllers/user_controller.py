from app.models.user import User
from app.database.database import db
from flask import jsonify ,request
from ..logs.logger import logger
import bcrypt
from flask_jwt_extended import create_access_token
from email_validator import validate_email, EmailNotValidError
import re

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
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"token": access_token,
                        "user" : user.to_dict()})
    return jsonify({"message": "Usuario o contraseña invalida"}), 401

def protected_users():
    return jsonify({"message": "This is a protected route"})

#REGISTER USER
def register_user(data):
    """
    Función para registrar un nuevo usuario con validaciones completas
    Maneja el proceso completo de registro según los criterios de aceptación
    """
    try:
        data = request.json

        #Verificar que todos los campos requeridos estén presentes
        required_fields = ["name", "last_name", "email", "password", "confirm_password"]
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({
                    "success": False,
                    "message": f"El campo '{field}' es obligatorio"}), 400
            
        # Extraer los datos
        name = data["name"].strip()
        last_name = data["last_name"].strip()
        email = data["email"].strip().lower()
        password = data["password"]
        confirm_password = data["confirm_password"]

        # Validación de nombres y apellidos
        if len(name) < 3:
            return jsonify({
                "success": False,
                "message": "El nombre debe tener al menos 3 carcateres"}), 400

        if len(last_name) < 3:
            return jsonify({
                "success": False,
                "message": "El apellido debe tener al menos 3 caracteres"}), 400

        # Validación de email
        try:
            #validate_email verifica el formato del email y existencia del dominio
            validation = validate_email(email)
            email = validation.email  # Normaliza el email   
        except EmailNotValidError as e:
            return jsonify({
                "success": False,
                "message": "Email inválido"}), 400
        
        # Validación de contraseña
        if len(password) < 8:
            return jsonify({
                "success": False,
                "message": "La contraseña debe tener al menos 8 caracteres"}), 400
        
        if not re.search(r"[A-Z]", password):
            return jsonify({
                "success": False,
                "message": "La contraseña debe contener al menos una letra mayúscula"}), 400
        
        if not re.search(r"[0-9]", password):
            return jsonify({
                "success": False,
                "message": "La contraseña debe contener al menos un número"}), 400
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return jsonify({
                "success": False,
                "message": "La contraseña debe contener al menos un caracter especial"}), 400
        
        if password != confirm_password:
            return jsonify({
                "success": False,
                "message": "Las contraseñas no coinciden"}), 400
        
        # Verificar si el email ya está registrado
        existing_user = User.query.filter_by(email=email).first()  
        if existing_user:
            return jsonify({
                "success": False,
                "message": "Ya existe un usario registrado con este email"}), 400
        
        # Crear el nuevo usuario
        new_user = User(
            name=name,
            last_name=last_name,
            email=email
        )
        new_user.set_password(password) #Establece la contraseña hasheada

        #Guardar el usuario en la base de datos
        db.session.add(new_user) 
        db.session.commit()

        logger.info(f"Usuario registrado exitosamente: {new_user.email}")

        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
        }), 201
    
    except Exception as e:
        logger.error(f"Error al registrar usuario: {str(e)}")
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({
            "success": False,
            "message": "Error al registrar usuario"}), 500

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from .config import DATABASE_URL, CORS_ORIGINS
from .database import db
from .models import Message, User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
CORS(app, origins=CORS_ORIGINS)
db.init_app(app)
bcrypt = Bcrypt(app)  # Se inicializa Bcrypt

@app.route("/message", methods=["POST"])
def post_message():
    data = request.json
    msg = Message(content=data["content"])
    db.session.add(msg)
    db.session.commit()
    return jsonify({"id": msg.id, "content": msg.content}), 201

@app.route("/message", methods=["GET"])
def get_messages():
    msgs = Message.query.all()
    return jsonify([{"id": m.id, "content": m.content} for m in msgs])


# 🆕 Ruta de prueba para registrar usuario
@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    nombre = data.get("nombre")
    correo = data.get("correo")
    contrasena = data.get("contrasena")

    if not nombre or not correo or not contrasena:
        return jsonify({"error": "Faltan datos requeridos"}), 400

    # Validar si ya existe el correo
    if User.query.filter_by(correo=correo).first():
        return jsonify({"error": "El correo ya está registrado"}), 409

    # Crear el nuevo usuario
    new_user = User(nombre=nombre, correo=correo, contrasena=contrasena)
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({
            "id": new_user.id,
            "nombre": new_user.nombre,
            "correo": new_user.correo,
            "fecha_creacion": new_user.fecha_creacion
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al registrar usuario"}), 500

# 🆕 Ruta de prueba para obtener todos los usuarios
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([
        {
            "id": user.id,
            "nombre": user.nombre,
            "correo": user.correo,
            "fecha_creacion": user.fecha_creacion
        }
        for user in users
    ])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea las tablas definidas en los modelos
    app.run(host="0.0.0.0", port=5000)

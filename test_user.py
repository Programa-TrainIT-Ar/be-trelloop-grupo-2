from app.main import app, db
from app.models import User

with app.app_context():
    # Crear un usuario de prueba
    new_user = User(
        nombre="Alejandro Prueba",
        correo="alejandro.prueba@example.com",
        contrasena="password123"
    )
    db.session.add(new_user)
    try:
        db.session.commit()
        print(f"Usuario {new_user.correo} creado con éxito.")
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear usuario: {e}")

    # Intentar crear un usuario con el mismo correo (debe fallar)
    duplicate_user = User(
        nombre="Otro Usuario",
        correo="alejandro.prueba@example.com",
        contrasena="password456"
    )
    db.session.add(duplicate_user)
    try:
        db.session.commit()
        print("¡Error! Se creó un usuario con correo duplicado.")
    except Exception as e:
        db.session.rollback()
        print(f"Correcto, no se permitió correo duplicado: {e}")

    # Ver todos los usuarios
    users = User.query.all()
    for user in users:
        print(f"Usuario: {user.nombre}, Correo: {user.correo}, Fecha: {user.fecha_creacion}")

# 🚀 INSTALACIÓN DEL PROYECTO

Sigue estos pasos para clonar y preparar el proyecto en tu entorno local:

### 0. Clonar el repositorio

```bash 
git clone https://github.com/Programa-TrainIT-Ar/be-trelloop-grupo-2.git
```
### 0.1. Ingresar al directorio del proyecto
```bash 
cd be-trelloop-grupo-2
```

### 1. Crear un entorno virtual en el root

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

```bash
source venv/Scripts/activate
```

### 3. Instalar requirements.txt

```bash
pip install -r requirements.txt
```

### 4. Crear la varialble de entorno desde el root para flask migrations (git bash)

```bash
export FLASK_APP=app.main:app
```

### 5. Crear nuevamente la base de datos y conectarla en el .env

### 6. Definir las variables requeridas en un .env. Las variables necesarias estan en .env.example

### 7. Traer las migraciones

```bash
flask db upgrade
```

### 8. Cargar usuarios de prueba en la base de datos

```bash
python -m app.seed_users
```
### 9. Inicializar la aplicacion flask.

```bash
python -m app.main
```

---

# 📚 DOCUMENTACIÓN DE ENDPOINTS

Esta sección describe todos los endpoints disponibles en la API del proyecto.

## 🔐 Autenticación

La API utiliza JWT (JSON Web Tokens) para la autenticación. Para acceder a endpoints protegidos, incluye el token en el header de autorización:

```
Authorization: Bearer <tu_token_jwt>
```



## 👥 Endpoints de Usuarios


### Obtener todos los usuarios
```http
GET /api/users/
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Iniciar sesión
```http
POST /api/users/login
```

**Body:**
```json
{
    "email": "juan@ejemplo.com",
    "password": "password123"
}
```

**Respuesta exitosa (200):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "name": "Juan",
    "last_name": "Pérez",
    "email": "juan@ejemplo.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Errores posibles:**
- `400`: Falta el correo o la contraseña
- `401`: Usuario o contraseña inválida
- `404`: Usuario no encontrado

### Ruta protegida (requiere autenticación)
```http
GET /api/users/protected
```

**Headers requeridos:**
```
Authorization: Bearer <token_jwt>
```

**Respuesta exitosa (200):**
```json
{
  "message": "This is a protected route"
}
```
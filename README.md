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

## 👥 Endpoints de registro
### Registrar nuevo usuario
### Este endpoint no requiere autenticación (es público).
```
POST /api/users/register
```
### Descripción:
**Registra un nuevo usuario en el sistema con validaciones completas para los datos proporcionados.**

**Body:**
```JSON

{
    "name": "Juan",
    "last_name": "Perez",
    "email": "juan.perez@example.com",
    "password": "Password123!",
    "confirm_password": "Password123!"
}
```

**Respuesta exitosa (201 - Created):**

```JSON

{
  "success": true,
  "message": "Usuario registrado exitosamente"
}
```

**Errores posibles (400 - Bad Request):**

El endpoint puede devolver un código 400 con mensajes específicos indicando la causa del error en el campo message.

Faltan campos obligatorios:
```JSON

{
  "success": false,
  "message": "El campo 'name' es obligatorio"
}
```
(o last_name, email, password, confirm_password si falta alguno).

**Nombre/Apellido inválido:**
```JSON

{
  "success": false,
  "message": "El nombre debe tener al menos 3 caracteres"
}
```
```JSON

{
  "success": false,
  "message": "El apellido debe tener al menos 3 caracteres"
}
```
**Correo electrónico inválido:**
```JSON

{
  "success": false,
  "message": "Email inválido"
}
```
**Contraseña demasiado corta:**
```JSON

{
  "success": false,
  "message": "La contraseña debe tener al menos 8 caracteres"
}
```
**Contraseña sin mayúscula:**
```JSON

{
  "success": false,
  "message": "La contraseña debe contener al menos una letra mayúscula"
}
```
**Contraseña sin número:**
```JSON

{
  "success": false,
  "message": "La contraseña debe contener al menos un número"
}
```
**Contraseña sin carácter especial:**
```JSON

{
  "success": false,
  "message": "La contraseña debe contener al menos un caracter especial"
}
```
**Contraseñas no coinciden:**
```JSON

{
  "success": false,
  "message": "Las contraseñas no coinciden"
}
```
**Email ya registrado:**
```JSON

{
  "success": false,
  "message": "Ya existe un usuario registrado con este email"
}
```
**Error general (500 - Internal Server Error):**

**Error interno del servidor:**
```JSON

{
  "success": false,
  "message": "Error al registrar usuario"
}
```
# 🚀 INSTALACIÓN DEL PROYECTO

Sigue estos pasos para preparar el proyecto en tu entorno local:

### 0.1 Inicializar el repositorio con git init

```bash
git init
```

### 0.1. En la carpeta inicializada

```bash
git remote add origin https://github.com/Programa-TrainIT-Ar/be-trelloop-grupo-2
```

### 0.2. Hacer un git pull

```bash
git pull origin main
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

Bienvenido a la documentación interactiva de la API de Trelloop. Aquí encontrarás toda la información necesaria para interactuar con nuestros servicios, desde la autenticación de usuarios hasta la gestión de tableros, listas y tarjetas.

## Accediendo a la Documentación
Nuestra API está documentada utilizando Swagger UI, lo que te permite explorar y probar los endpoints directamente desde tu navegador.

## URL de la Documentación
Una vez que la aplicación esté corriendo localmente, puedes acceder a la documentación en la siguiente URL:

http://localhost:5000/docs/

## Uso de Swagger UI
La interfaz de Swagger UI organiza los endpoints por etiquetas (tags), como "Authentication", "Boards", etc. Para usar la API, sigue estos pasos:

### 1. Autenticación (Obtener un Token JWT)
Para interactuar con la mayoría de los endpoints de la API, necesitarás un token de autenticación JWT.

Paso a Paso:

1. Dirígete a la sección "Authentication" en la documentación.

2. Expande el endpoint POST /api/login.

3. Haz clic en "Try it out".

4. Introduce tus credenciales de usuario (correo y contraseña) en el campo body.

5. Haz clic en "Execute".

6. En la sección de Responses, verás la respuesta de la API que incluirá tu token JWT. Cópialo (será una cadena larga).

### 2. Autorizar Solicitudes
Una vez que tengas tu token JWT, deberás usarlo para autorizar tus solicitudes a los endpoints protegidos:

#### Paso a Paso:

1. En la parte superior de la página de Swagger UI, haz clic en el botón "Authorize".

2. Aparecerá una ventana de diálogo para la BearerAuth.

3. En el campo de entrada, escribe la palabra Bearer seguida de un espacio y luego pega tu token JWT.

- Ejemplo: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODg5NzY5OSwianRpIjoiZmVkMjAxOWUtODk2Yi00NmY0LWEyZmQtYjY2ZjQwYzE3ZDMxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjc4ODk3Njk5LCJleHAiOjE2Nzg4OTg1OTl9.your_jwt_token_here

4. Haz clic en "Authorize" y luego en "Close".

5. Verás que los iconos de candado junto a los endpoints protegidos ahora aparecerán "cerrados" o "autorizados".

### 3. Probar Endpoints Protegidos
Ahora que estás autorizado, puedes probar los demás endpoints:

- Paso a Paso:

1. Expande cualquier endpoint que tenga el icono de candado "cerrado" (indicando que requiere autenticación), por ejemplo, GET /api/boards/.

2. Haz clic en "Try it out".

3. Si el endpoint requiere parámetros (como board_id en GET /api/boards/{board_id} o un body para POST/PUT), introduce los valores necesarios.

4. Haz clic en "Execute".

5. Revisa la Response body para ver el resultado de tu solicitud.

Estructura de la Documentación
Authentication: Endpoints relacionados con el registro, inicio de sesión y gestión de sesiones de usuario.

Boards: Endpoints para crear, obtener, actualizar y eliminar tableros.

[Otros Tags]: Si tienes más secciones (e.g., Lists, Cards, Users), serán listadas aquí con sus respectivos endpoints.

Esperamos que esta guía te sea de gran utilidad para explorar y utilizar la API de Trelloop. Si tienes alguna pregunta o encuentras algún problema, no dudes en contactarnos.

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

## 🗂️ Endpoints de Usuarios

### Obtener todos los tableros creados

### Este endpoint no requiere autenticación (es público).

```
GET /api/boards
```

### Descripción:

**Este endpoint permite obtener todos los tableros creados por todos los usuarios.
.**

**Respuesta exitosa (200 - OK):**

```JSON
[
  {
    "board_image_url": "https://proyectoEjemplo.com",
    "created_at": "2025-07-23T00:00:00",
    "description": "Esta es un board de ejemplo",
    "id": 1,
    "members": [
      {
        "email": "juan@gmail.com",
        "id": 1,
        "last_name": "Perez",
        "name": "Juan"
      },
      {
        "email": "juanita@gmail.com",
        "id": 2,
        "last_name": "Perez",
        "name": "Juanita"
      }
    ],
    "name": "Board 1",
    "owner_id": 1,
    "status": "private",
    "tags": []
  },
  {
    "board_image_url": "https://proyectoEjemplo2.com",
    "created_at": "2025-07-24T15:12:02.414133",
    "description": "Esta es otro board de ejemplo",
    "id": 2,
    "members": [
      {
        "email": "juanita@gmail.com",
        "id": 2,
        "last_name": "Perez",
        "name": "Juanita"
      }
    ],
    "name": "Board 2",
    "owner_id": 2,
    "status": "public",
    "tags": [
      "frontend",
      "backend",
      "urgente"
    ]
  }
]

```

**Errores posibles (500 - Internal Server Error):**

### Obtener tablero por ID

### Este endpoint no requiere autenticación (es público).

```
GET /api/boards/{id}
```

### Descripción:

**Este endpoint permite obtener un único tablero según su identificador.
.**

**Respuesta exitosa (200 - OK):**

```JSON
[
  {
    "board_image_url": "https://proyectoEjemplo.com",
    "created_at": "2025-07-23T00:00:00",
    "description": "Esta es un board de ejemplo",
    "id": 1,
    "members": [
      {
        "email": "juan@gmail.com",
        "id": 1,
        "last_name": "Perez",
        "name": "Juan"
      },
      {
        "email": "juanita@gmail.com",
        "id": 2,
        "last_name": "Perez",
        "name": "Juanita"
      }
    ],
    "name": "Board 1",
    "owner_id": 1,
    "status": "private",
    "tags": []
  }
  ]

```

**Errores posibles (500 - Internal Server Error):**
**Errores posibles (404 - Board no encontrada):**

### Crear un tablero

### Este endpoint requiere autenticación (no es público).

```
POST /api/boards
```

### Descripción:

**Este endpoint permite crear un nuevo tablero para un usuario autenticado, incluyendo su nombre,imagen , descripción y estado, el cual debe ser "private" o "public". También se debe proporcionar una lista de miembros (usuarios ya registrados) que serán añadidos al tablero, así como una lista de etiquetas (tags); si una etiqueta no existe en la base de datos, se crea automáticamente, y si ya existe, se reutiliza.
.**
**Respuesta exitosa (201 - CREATED):**

### Payload

```JSON
{
"name": "Tablero Prueba",
"description": "Este es un tablero de prueba",
"status": "private",
"boardImageUrl": "https://tableroPrueba.com",
"members": [3, 4],
"tags": ["Web", "backend", "cocina"]
}
```

**Errores posibles (500 - Internal Server Error):**
**Errores posibles (401 - UNAUTHORIZED):**
**Falta nombre de tablero (400 - BAD REQUEST):**

### Obtener tableros de un usuario autenticado

### Este endpoint requiere autenticación (no es público).

```
GET /api/boards/member
```

### Descripción:

**Este endpoint permite obtener todos los tableros en los que el usuario autenticado es miembro, incluyendo aquellos que ha creado, ya que al crear un tablero automáticamente se le asigna como miembro.
.**

**Respuesta exitosa (200 - CREATED):**

```JSON
{
  "boards": [
    {
    "created_at": "2025-07-28T02:47:30.761384",
    "id": 1,
    "name": "Tablero Prueba 1"
    },
    {
    "created_at": "2025-07-28T02:51:21.348853",
    "id": 2,
    "name": "Tablero Prueba 2"
    },
    {
    "created_at": "2025-07-29T15:17:07.531928",
    "id": 3,
    "name": "Tablero Prueba 3"
    }
  ]
}
```

**Errores posibles (500 - Internal Server Error):**
**Errores posibles (401 - UNAUTHORIZED):**

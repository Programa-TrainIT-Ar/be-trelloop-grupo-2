from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..controllers.user_controller import get_users, login_users, protected_users
from flasgger.utils import swag_from

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'security': [{'BearerAuth': []}], # This endpoint requires authentication
    'description': 'Obtiene una lista de todos los usuarios registrados',
    'responses': {
        200: {
            'description': 'Lista de usuarios',
            'examples': {
                'application/json': [
                    {
                        "boards": [
                            {"name": "Tablero 1"},
                            {"name": "Tablero 2"},
                            {"name": "Tablero 3"}
                        ],
                        "created_at": "2025-07-24T19:24:58.914235",
                        'id': 1,
                        'name': 'Maria',
                        'last_name': 'Martinez',
                        'email': 'Maria@Martinez.com'
                    },
                    {
                        "boards": [
                            {"name": "Tablero 1"},
                            {"name": "Tablero 2"},
                            {"name": "Tablero 3"}
                        ],
                        "created_at": "2025-08-24T19:24:58.914235",
                        'id': 2,
                        'name': 'Juan',
                        'last_name': 'Perez',
                        'email': 'juan@Perez.com'
                    },
                ]
            }
        }
    }
})
def list_users():
    return get_users()


@user_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    # Login usually doesn't require a token for itself, remove 'security' if not needed
    # If your login endpoint returns a token, it's typically an unsecured endpoint
    # 'security': [{'BearerAuth': []}], # Remove this line for login if it's the endpoint to get a token
    'summary': 'Login de usuario',
    'description': 'Inicia sesión con email y password',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'example': 'admin@example.com'},
                    'password': {'type': 'string', 'example': '123456'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login exitoso',
            'examples': {
                'application/json': {
                    'token': 'JWT_TOKEN',
                    'user': {'id': 1, 'email': 'admin@example.com', "last_name": "example", "name": "Admin"}
                }
            }
        },
        401: {'description': 'Credenciales incorrectas'},
        400: {'description': 'Faltan campos obligatorios'},
        404: {'description': 'Usuario no encontrado'}
    }
})
def handle_login_users():
    return login_users()



@user_bp.route('/protected', methods=['GET'])
@jwt_required()
def handle_protected_users():
    return protected_users()


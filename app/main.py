from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from .config.config import config
from .database.database import db
#ACA SE IMPORTAN LOS MODELOS PARA SER DETECTADOS POR FLASK-MIGRATE
from .models import User, Board , List, Card, CardComment, CardAssignee, UserBoard, Tag
from .routes import all_blueprints
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flasgger import Swagger


app = Flask(__name__)
app.config['SWAGGER'] = {
    "swagger_version": "2.0", 
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  
            "model_filter": lambda tag: True,  
        }
    ],
    "swagger_ui": True,
    "specs_route": "/docs/", 
    "securityDefinitions": {
        "BearerAuth": { 
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    },
    # this is here to apply to all secured endpoints by default, or specify per route
    "security": [{"BearerAuth": []}] 
}

swagger = Swagger(app)

app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = config["DATABASE_URL"]
app.config["JWT_SECRET_KEY"] = config["JWT_SECRET_KEY"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=config["JWT_ACCESS_TOKEN_EXPIRES"])
CORS(app, origins=config["CORS_ORIGINS"])

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


for bp in all_blueprints:
    app.register_blueprint(bp)

if __name__ == "__main__":
     app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from .config.config import config
from .database.database import db
#ACA SE IMPORTAN LOS MODELOS PARA SER DETECTADOS POR FLASK-MIGRATE
from .models import User, Board , List, Card, CardComment, CardAssignee
from .routes import all_blueprints
from flask_jwt_extended import JWTManager
from datetime import timedelta

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = config["JWT_SECRET_KEY"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=config["JWT_ACCESS_TOKEN_EXPIRES"])
app.config["SQLALCHEMY_DATABASE_URI"] = config["DATABASE_URL"]
CORS(app, origins=config["CORS_ORIGINS"])

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


for bp in all_blueprints:
    app.register_blueprint(bp)

if __name__ == "__main__":
     app.run(host="0.0.0.0", port=5000)

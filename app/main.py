from flask import Flask, request, jsonify
from flask_cors import CORS
from .config import DATABASE_URL, CORS_ORIGINS
from .database import db
from .models import User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
CORS(app, origins=CORS_ORIGINS)
db.init_app(app)

# User routes
@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(
        name=data['name'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

if __name__ == "__main__":
     with app.app_context():
          db.create_all()
     app.run(host="0.0.0.0", port=5000)

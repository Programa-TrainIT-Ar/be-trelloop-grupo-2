from .user_routes import user_bp  # si tienes más
from .register import register_bp

all_blueprints = [
    register_bp,
    user_bp,]
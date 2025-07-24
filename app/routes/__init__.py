from .user_routes import user_bp  # si tienes más
from .register import register_bp
from .board_routes import board_bp

all_blueprints = [
    register_bp,
    board_bp,
    user_bp,]
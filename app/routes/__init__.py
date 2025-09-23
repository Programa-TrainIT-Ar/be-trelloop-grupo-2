from .user_routes import user_bp  # si tienes más
from .register import register_bp
from .board_routes import board_bp
from .list_routes import list_bp
from .card_routes import card_bp
from .comments_routes import comment_bp

all_blueprints = [
    register_bp,
    board_bp,
    list_bp,
    card_bp,
    comment_bp,
    user_bp,]
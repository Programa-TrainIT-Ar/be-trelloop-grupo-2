from ..logs.logger import logger
import os
from dotenv import load_dotenv
load_dotenv()

def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        return logger.error(f"Falta la variable de entorno {name}")
    return value

config = {
    "DATABASE_URL" : get_env_variable("DATABASE_URL"),
    "JWT_SECRET_KEY" : get_env_variable("JWT_SECRET_KEY"),
    "CORS_ORIGINS" : get_env_variable("CORS_ORIGINS").split(","),
    "JWT_ACCESS_TOKEN_EXPIRES": int(get_env_variable("JWT_ACCESS_TOKEN_EXPIRES")),

    "CLOUDINARY_CLOUD_NAME": get_env_variable("CLOUDINARY_CLOUD_NAME"),
    "CLOUDINARY_API_KEY": get_env_variable("CLOUDINARY_API_KEY"),
    "CLOUDINARY_API_SECRET": get_env_variable("CLOUDINARY_API_SECRET"),

    "PUSHER_APP_ID": get_env_variable("PUSHER_APP_ID"),
    "PUSHER_KEY": get_env_variable("PUSHER_KEY"),
    "PUSHER_SECRET": get_env_variable("PUSHER_SECRET"),
    "PUSHER_CLUSTER": get_env_variable("PUSHER_CLUSTER", "us2"),

    "RESEND_API_KEY": get_env_variable("RESEND_API_KEY"),
    "RESEND_FROM_EMAIL": get_env_variable("RESEND_FROM_EMAIL", "notifications@trainit.com"),
    "FRONTEND_URL": get_env_variable("FRONTEND_URL", "http://localhost:3000"),
}



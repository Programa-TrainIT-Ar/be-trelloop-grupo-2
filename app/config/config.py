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
}



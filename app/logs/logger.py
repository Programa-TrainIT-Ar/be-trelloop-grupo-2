from loguru import logger
import sys

logger.remove()

logger.add(
    sys.stderr,  
    level="DEBUG", 
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
    colorize=True,
)
# logger.info("Este es un mensaje de informacion")
# logger.success("Este es un mensaje de éxito")
# logger.warning("Este es un mensaje de advertencia")
# logger.error("Este es un mensaje de error")
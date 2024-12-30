import logging
from dotenv import load_dotenv
from rich.logging import RichHandler

def setup_environment_and_logging():
    load_dotenv()
    logger = logging.getLogger("rich")
    if not logger.handlers:
        FORMAT = "%(message)s"
        logging.basicConfig(level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

    return logger
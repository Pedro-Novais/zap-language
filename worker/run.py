import os
import sys
from dotenv import load_dotenv
load_dotenv()

from celery.signals import after_setup_logger

from external.container.celery import app_celery
from worker import worker

from loguru import logger


logger.remove()


env_production = os.getenv("ENV") == "production"

@after_setup_logger.connect
def setup_celery_logger(logger, *args, **kwargs):
    config_logger()
    
def config_logger() -> None:
    logger.remove()
    
    if not env_production:
        logger.add(
            sys.stderr, 
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
            colorize=True
        )
        logger.add("logs/local_debug.log", rotation="10 MB", retention="3 days")
    else:
        logger.add(sys.stdout, serialize=True, level="INFO", enqueue=True)

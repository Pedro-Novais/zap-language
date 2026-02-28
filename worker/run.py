from dotenv import load_dotenv
load_dotenv()

from external.container.celery import app_celery
from worker import worker
from app import create_app, worker, db
from loguru import logger

from dotenv import load_dotenv

load_dotenv()

application = create_app()

if __name__ == "__main__":
    with application.app_context():
        logger.info("👷 Worker de Produção iniciado...")
        worker.run()
        
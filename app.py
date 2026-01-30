import sys
import os
from loguru import logger
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

from external.routes import Routes

logger.remove()


def main() -> None:
    
    load_dotenv()
    config_logger()
    
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    
    CORS(
        app=app, 
        resources={r"/api/*": {"origins": "*"}}, 
        headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        supports_credentials=True,
    )
    
    routes = Routes(app=app)
    routes.register_error_handlers()
    routes.build_routes()
    
    port = int(os.getenv("PORT"))
    app.run(
        debug=True,
        host="0.0.0.0",
        port=port
    )

def config_logger() -> None:
    if os.getenv("ENV") != "production":
        logger.add(
            sys.stderr, 
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
            colorize=True
        )
        logger.add("logs/local_debug.log", rotation="10 MB", retention="3 days")
    else:
        logger.add(sys.stdout, serialize=True)


if __name__ == "__main__":     
    try:
        main()
    except Exception as e:
        print(f"Erro ao inicializar: {e}")
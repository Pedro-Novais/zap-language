from dotenv import load_dotenv
load_dotenv()

import sys
import os

from loguru import logger
from flask import Flask
from flask_cors import CORS

from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from external.routes import Routes
from external.database.models import(
    StudySettings,
    User,
    PhoneVerification,
    Subscription,
    Plan,
    MessageHistory,
    SystemConfig,
)

logger.remove()

env_production = os.getenv("ENV") == "production"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def create_app():
    config_logger()
    
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
    
    return app

def config_logger() -> None:
    if not env_production:
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
        application = create_app()
        port = int(os.getenv("PORT", 5000))
        application.run(debug=not env_production, host="0.0.0.0", port=port, use_reloader=False)
    except Exception as e:
        print(f"Erro ao inicializar: {e}")

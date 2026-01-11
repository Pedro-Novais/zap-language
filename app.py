import os

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from external.routes import Routes


def main() -> None:
     
     load_dotenv()
     app = Flask(__name__)
     CORS(
          app=app, 
          resources={r"/api/*": {"origins": "*"}}, 
          headers=['Content-Type', 'Authorization'],
          methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
          supports_credentials=True,
     )

     Routes(app=app).build_routes()
     app.run(
          debug=True,
          host="0.0.0.0",
          port=os.getenv("PORT")
     )

if __name__ == "__main__":
     try:
          main()
     
     except Exception as e:
          print("Erro ao inicializar a aplicação, erro: {}".format(e))
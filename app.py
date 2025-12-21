from flask import Flask
from flask_cors import CORS

from external.routes import Routes


def main() -> None:
     
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
          port=5000
     )

if __name__ == "__main__":
     try:
          main()
     
     except Exception as e:
          print("Erro ao inicializar a aplicação, erro: {}".format(e))
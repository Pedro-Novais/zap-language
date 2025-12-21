from flask import Flask

from ._UserRoute import UserRoute

class Routes:

    def __init__(
            self,
            app: Flask,
        ) -> None:

        self.app = app

    def build_routes(
            self,
        ) -> None:

        UserRoute(app=self.app).register_routes()
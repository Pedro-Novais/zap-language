from flask import Flask, app

from external.utils.error_handled_request import register_error_handlers
from external.routes.user_routes import UserRoute
from external.routes.zapi_routes import ZapiRoute
from external.routes.study_settings_routes import StudySettingsRoute


class Routes:

    BASE_ROUTE_NAME = '/api'
    BASE_ROUTE_VERSION_1 = '/v1'
    
    def __init__(
        self,
        app: Flask,
    ) -> None:

        self.app = app
        base_route_v1 = f'{self.BASE_ROUTE_NAME}{self.BASE_ROUTE_VERSION_1}'
        
        self.user_route = UserRoute(
            app=app,
            base_route=base_route_v1,
        )
        self.zapi_route = ZapiRoute(
            app=app,
            base_route=base_route_v1,
        )
        self.study_settings_route = StudySettingsRoute(
            app=app,
            base_route=base_route_v1,
        )

    def build_routes(
        self,
    ) -> None:

        self.user_route.register_routes()
        self.zapi_route.register_routes()
        self.study_settings_route.register_routes()

    def register_error_handlers(
        self,
    ) -> None:

        register_error_handlers(app=self.app)
    
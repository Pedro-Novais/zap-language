from flask import Flask, app, jsonify

from external.utils.error_handled_request import register_error_handlers
from external.routes.user_routes import UserRoute
from external.routes.auth_routes import AuthRoute
from external.routes.zapi_routes import ZapiRoute
from external.routes.study_settings_routes import StudySettingsRoute
from external.routes.plan_routes import PlanRoute
from external.routes.scenario_routes import ScenarioRoute
from external.routes.subscription_routes import SubscriptionRoute


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
        self.auth_route = AuthRoute(
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
        self.plan_route = PlanRoute(
            app=app,
            base_route=base_route_v1,
        )
        self.scenario_route = ScenarioRoute(
            app=app,
            base_route=base_route_v1,
        )
        self.subscription_route = SubscriptionRoute(
            app=app,
            base_route=base_route_v1,
        )

    def build_routes(
        self,
    ) -> None:

        # Health check endpoint sem autenticação para testar CORS
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "ok", "message": "API is running"}), 200

        self.user_route.register_routes()
        self.auth_route.register_routes()
        self.zapi_route.register_routes()
        self.study_settings_route.register_routes()
        self.plan_route.register_routes()
        self.scenario_route.register_routes()
        self.subscription_route.register_routes()

    def register_error_handlers(
        self,
    ) -> None:

        register_error_handlers(app=self.app)
    
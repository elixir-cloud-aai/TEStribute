"""
Service for the TEStribute.
"""
import os

from connexion import App

from TEStribute.config.parse_config import config_parser
from TEStribute.errors import (register_error_handlers)

# Instantiate app
app = App(__name__)

# Get config
config = config_parser(
    os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "config/server_config.yaml"
        )
    )
)


def configure_app(app: App) -> App:
    """Configure app"""
    app = add_settings(app)
    app = register_error_handlers(app)
    app = add_openapi(app)
    return app


def add_settings(app: App) -> App:
    """Add settings to app instance"""
    app.host = config["server"]["host"]
    app.port = config["server"]["port"]
    app.debug = config["server"]["debug"]
    return app


def add_openapi(app: App) -> App:
    """Add OpenAPI specification to app instance"""
    app.add_api(
        config["openapi"]["TEStribute"],
        validate_responses=True,
        strict_validation=True
    )
    return app


def main(app: App) -> None:
    """Initialize, configure and run server"""
    app = configure_app(app)
    app.run()


if __name__ == "__main__":
    main(app)

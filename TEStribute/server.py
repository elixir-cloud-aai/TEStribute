"""
Service for the TEStribute.
"""
import os

from connexion import App

from TEStribute.config.parse_config import config_parser
from TEStribute.errors import (register_error_handlers)

app = App(__name__)

config = config_parser(
    os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "config/server_config.yaml"
        )
    )
)


def configure_app(app):
    """Configure app"""

    # Add settings
    app = add_settings(app)

    # Register error handlers
    app = register_error_handlers(app)

    # Add OpenAPIs
    app = add_openapi(app)

    return app


def add_settings(app):
    """Add settings to Flask app instance"""
    app.host = config["server"]["host"]
    app.port = config["server"]["port"]
    app.debug = config["server"]["debug"]

    return app


def add_openapi(app):
    """Add OpenAPI specification to connexion app instance"""
    app.add_api(
        config["openapi"]["TEStribute"], validate_responses=True, strict_validation=True
    )

    return app


def main(app):
    """Initialize, configure and run server"""
    app = configure_app(app)
    app.run()


if __name__ == "__main__":
    main(app)

"""
Service for the TEStribute.
"""
import os
from shutil import copyfile

from connexion import App

from TEStribute.config.parse_config import config_parser
from TEStribute.errors import (register_error_handlers)
from TEStribute.security.process_jwt import JWT

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
    app.app.config.update(config)
    return app


def add_openapi(app: App) -> App:
    """Add OpenAPI specification to app instance"""
    path = os.path.join(
        os.path.abspath(
            os.path.dirname(
                os.path.realpath(__file__)
            )
        ),
        config["openapi"]["TEStribute"]
    )
    if config["security"]["authorization_required"]:
        path = add_security_definitions(in_file=path)
        JWT.config(**config["security"]["jwt"])
    app.add_api(
        path,
        validate_responses=True,
        strict_validation=True
    )
    return app


def add_security_definitions(
    in_file: str,
    ext: str = 'security_definitions_added.yaml'
) -> str:
    """Adds 'securityDefinitions' section to OpenAPI YAML specs."""
    # Set security definitions
    amend = '''

# Amended by WES-ELIXIR
  securitySchemes:
    jwt:
      type: http
      scheme: bearer
      bearerFormat: JWT
      x-bearerInfoFunc: security.process_jwt.connexion_bearer_info

security:
- jwt: []
'''

    # Create copy for modification
    out_file: str = '.'.join([os.path.splitext(in_file)[0], ext])
    copyfile(in_file, out_file)

    # Append security definitions
    with open(out_file, 'a') as mod:
        mod.write(amend)

    return out_file


def main(app: App) -> None:
    """Initialize, configure and run server"""
    app = configure_app(app)
    app.run()


if __name__ == "__main__":
    main(app)

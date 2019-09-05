from connexion import App

app = App(
    __name__,
)


def configure_app(app):
    """Configure app"""

    # Add settings
    app = add_settings(app)

    # Add OpenAPIs
    app = add_openapi(app)

    return app


def add_settings(app):
    """Add settings to Flask app instance"""
    # TODO:
    #   read from config file ( possiby using TESTribute.parse_config functions)
    app.host = '0.0.0.0'
    app.port = '8080'
    app.debug = True

    return app


def add_openapi(app):
    """Add OpenAPI specification to connexion app instance"""
    # TODO:
    # read from config and accept error for corrupt file
    app.add_api(
            "specs/schema.TEStribute.openapi.yaml",
            validate_responses=True,
            strict_validation=True,
        )

    return app


def main(app):
    """Initialize, configure and run server"""
    app = configure_app(app)
    app.run()


if __name__ == '__main__':
    main(app)

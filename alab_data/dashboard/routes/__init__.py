from .basic_route import modules
from .sample import sample_bp


def init_app(app):
    """
    Add routes to the app
    """
    app.register_blueprint(modules)
    app.register_blueprint(sample_bp)

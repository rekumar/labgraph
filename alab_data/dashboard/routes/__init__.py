from .basic_route import modules
from .sample import sample_bp
from .nodes import material_bp, measurement_bp, analysis_bp, action_bp


def init_app(app):
    """
    Add routes to the app
    """
    app.register_blueprint(modules)
    app.register_blueprint(sample_bp)
    app.register_blueprint(material_bp)
    app.register_blueprint(measurement_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(action_bp)

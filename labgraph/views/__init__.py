from .base import BaseView
from .sample import SampleView
from .nodes import (
    MaterialView,
    ActionView,
    MeasurementView,
    AnalysisView,
    AnalysisMethodView,
    ActorView,
)


def get_view(node) -> BaseView:
    """Get the view corresponding to a given node type

    Args:
        node (Node): Node to get view for

    Returns:
        BaseNodeView: View for node
    """
    return get_view_by_type(node.__class__.__name__)


def get_view_by_type(node_type: str) -> BaseView:
    """Get the view corresponding to a given node type

    Args:
        type (str): Node/Actor/Sample type to get view for

    Returns:
        BaseNodeView: View for type
    """
    VIEWS = {
        "Action": ActionView,
        "Analysis": AnalysisView,
        "AnalysisMethod": AnalysisMethodView,
        "Actor": ActorView,
        "Measurement": MeasurementView,
        "Material": MaterialView,
        "Sample": SampleView,
    }
    if node_type not in VIEWS:
        raise ValueError(
            f"Invalid node type: {node_type}. Must be one of {VIEWS.keys()}"
        )
    return VIEWS[node_type]()

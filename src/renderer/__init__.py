"""Editable PPTX renderer package for GroundedDeck."""

from src.renderer.artifact_grader import grade_pptx_artifact
from src.renderer.pptx_renderer import (
    get_supported_layouts,
    render_slide_spec_to_pptx,
)
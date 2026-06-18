"""spllint: lint and format Splunk SPL searches for correctness and performance."""
from .parse import split_pipeline, Stage
from .rules import lint, Finding
from .format import format_spl
__all__ = ["split_pipeline", "Stage", "lint", "Finding", "format_spl"]
__version__ = "0.2.0"

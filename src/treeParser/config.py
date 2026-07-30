"""
Parser configuration.

All configurable values are centralized here so the parser behavior
can be changed without modifying the parser implementation.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ParserConfig:
    """
    Global parser configuration.
    """

    #
    # Chapter detection
    #

    chapter_start: str = "3 Command Trees"

    chapter_end: str = "4 Commands"

    #
    # Output
    #

    output_directory: Path = Path("output")

    output_filename: str = "command_trees.json"

    pretty_json: bool = True

    json_indent: int = 4

    #
    # Validation
    #

    validate_tree: bool = True

    #
    # PDF
    #

    merge_wrapped_lines: bool = True

    detect_indent_automatically: bool = True

    default_indent_width: float = 20.0

    #
    # Logging
    #

    log_level: str = "INFO"
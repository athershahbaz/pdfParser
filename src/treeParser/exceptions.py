"""
exceptions.py

Custom exception hierarchy for the Nokia Classic CLI parser.
"""

from __future__ import annotations


class NokiaCLIParserError(Exception):
    """
    Base exception for all parser-related errors.
    """
    pass


# ----------------------------------------------------------------------
# PDF Reader
# ----------------------------------------------------------------------

class PDFReaderError(NokiaCLIParserError):
    """
    Raised when the PDF cannot be opened or parsed.
    """
    pass


# ----------------------------------------------------------------------
# Tokenizer
# ----------------------------------------------------------------------

class TokenizerError(NokiaCLIParserError):
    """
    Raised when tokenization fails.
    """
    pass


# ----------------------------------------------------------------------
# Parser
# ----------------------------------------------------------------------

class ParserError(NokiaCLIParserError):
    """
    Raised when parsing fails.
    """
    pass


class InvalidIndentationError(ParserError):
    """
    Raised when an invalid indentation structure is detected.
    """
    pass


class InvalidSectionError(ParserError):
    """
    Raised when an invalid section hierarchy is detected.
    """
    pass


# ----------------------------------------------------------------------
# Semantic Analyzer
# ----------------------------------------------------------------------

class SemanticAnalyzerError(NokiaCLIParserError):
    """
    Raised when semantic analysis fails.
    """
    pass


# ----------------------------------------------------------------------
# Validator
# ----------------------------------------------------------------------

class ValidationError(NokiaCLIParserError):
    """
    Raised when validation fails.
    """
    pass


# ----------------------------------------------------------------------
# Exporter
# ----------------------------------------------------------------------

class ExportError(NokiaCLIParserError):
    """
    Raised when JSON export fails.
    """
    pass


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

class ConfigurationError(NokiaCLIParserError):
    """
    Raised when parser configuration is invalid.
    """
    pass
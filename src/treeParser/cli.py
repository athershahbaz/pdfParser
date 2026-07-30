"""
cli.py

Command-line interface for the Nokia Classic CLI parser.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from config import ParserConfig
from exporter import Exporter
from parser import Parser
from pdf_reader import PDFReader
from semantic_analyzer import SemanticAnalyzer
from tokenizer import Tokenizer
from validator import Validator

logger = logging.getLogger(__name__)


class CLI:
    """
    Command-line application.

    Pipeline:

        PDF
         ↓
      Reader
         ↓
     Tokenizer
         ↓
      Parser
         ↓
 Semantic Analyzer
         ↓
     Validator
         ↓
      Exporter
    """

    def __init__(self):

        self.config = ParserConfig()

    # ----------------------------------------------------------

    def build_argument_parser(
        self,
    ) -> argparse.ArgumentParser:

        parser = argparse.ArgumentParser(

            prog="nokia-cli-parser",

            description=(
                "Parse Nokia Classic CLI PDF "
                "and generate command hierarchy JSON."
            ),
        )

        parser.add_argument(

            "input",

            type=Path,

            help="Input Nokia CLI PDF file.",
        )

        parser.add_argument(

            "output",

            type=Path,

            help="Output JSON file.",
        )

        parser.add_argument(

            "--verbose",

            action="store_true",

            help="Enable verbose logging.",
        )

        return parser

    # ----------------------------------------------------------

    def run(
        self,
        argv: list[str] | None = None,
    ) -> int:

        parser = self.build_argument_parser()

        args = parser.parse_args(argv)

        logging.basicConfig(

            level=(
                logging.DEBUG
                if args.verbose
                else logging.INFO
            ),

            format=(
                "%(asctime)s "
                "%(levelname)s "
                "%(message)s"
            ),
        )

        try:

            self.execute(

                pdf_path=args.input,

                output_path=args.output,

            )

            logger.info("Completed successfully.")

            return 0

        except Exception:

            logger.exception("Parser failed.")

            return 1

    # ----------------------------------------------------------

    def execute(
        
        self,

        pdf_path: Path,

        output_path: Path,

    ) -> None:
        #modified it later by AI
        if not pdf_path.exists():

            raise FileNotFoundError(
                f"Input PDF file not found: {pdf_path}"
            )
        logger.info(
            "Reading PDF..."
        )

        reader = PDFReader(

            self.config,
        )

        pages = reader.read(

            pdf_path,
        )

        logger.info(
            "Tokenizing..."
        )

        tokenizer = Tokenizer(

            self.config,
        )

        tokens = tokenizer.tokenize(

            pages,
        )

        logger.info(
            "Parsing..."
        )

        parser = Parser(

            self.config,
        )

        parse_result = parser.parse(

            tokens,
        )

        logger.info(
            "Building command graph..."
        )

        analyzer = SemanticAnalyzer(

            self.config,
        )

        graph = analyzer.analyze(

            parse_result,
        )

        logger.info(
            "Validating..."
        )

        validator = Validator()

        report = validator.validate(

            graph,
        )

        if report.has_errors:

            logger.error(
                "Validation failed."
            )

            for message in report.messages:

                logger.error(

                    "[%s] %s : %s",

                    message.code,

                    message.path,

                    message.message,

                )

            raise RuntimeError(
                "Validation failed."
            )

        logger.info(
            "Exporting JSON..."
        )

        exporter = Exporter()

        exporter.export_json(

            graph,

            output_path,
        )
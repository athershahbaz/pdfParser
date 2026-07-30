"""
pdf_reader.py

Reads Nokia Classic CLI PDF documentation and reconstructs logical text lines
while preserving positional information.

This module is responsible ONLY for reading the PDF.

It does not:
    - detect chapters
    - parse command trees
    - normalize lines
    - build JSON

Dependencies
------------
pdfplumber

Author
------
ChatGPT
"""

from __future__ import annotations

import logging
from pathlib import Path
from collections import defaultdict

import pdfplumber

from config import ParserConfig
from models import (
    Page,
    Word,
    TextLine,
)

logger = logging.getLogger(__name__)


class PDFReader:
    """
    Reads a PDF document and reconstructs text lines.

    Each page is converted into:

        Page
            ├── Word
            └── TextLine

    Coordinates are preserved for later parser stages.
    """

    #
    # Maximum vertical distance between words
    # belonging to the same logical line.
    #
    LINE_TOLERANCE = 2.0

    #
    # Maximum horizontal gap before inserting
    # an extra space.
    #
    WORD_GAP = 3.0

    # -----------------------------------------------------------------

    def __init__(
        self,
        config: ParserConfig,
    ) -> None:

        self.config = config

    # -----------------------------------------------------------------

    def read(self) -> list[Page]:
        """
        Read the complete PDF.

        Returns
        -------
        list[Page]
        """

        pdf_path = self.config.pdf_file

        if pdf_path is None:
            raise ValueError("PDF file not configured.")

        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        logger.info("Reading PDF: %s", pdf_path)

        pages: list[Page] = []

        with pdfplumber.open(pdf_path) as pdf:

            for page_number, pdf_page in enumerate(
                pdf.pages,
                start=1,
            ):

                pages.append(
                    self._read_page(
                        page_number,
                        pdf_page,
                    )
                )

        logger.info(
            "Loaded %d pages.",
            len(pages),
        )

        return pages

    # -----------------------------------------------------------------

    def _read_page(
        self,
        page_number: int,
        pdf_page,
    ) -> Page:

        logger.debug(
            "Reading page %d",
            page_number,
        )

        words = self._extract_words(pdf_page)

        lines = self._reconstruct_lines(words)

        return self._finalize_page(
            page_number,
            words,
            lines,
        )

    # -----------------------------------------------------------------

    def _extract_words(
        self,
        pdf_page,
    ) -> list[Word]:
        """
        Extract words preserving coordinates.
        """

        result: list[Word] = []

        extracted = pdf_page.extract_words(
            keep_blank_chars=False,
            use_text_flow=True,
        )

        for item in extracted:

            result.append(
                Word(
                    text=item["text"],
                    x0=item["x0"],
                    x1=item["x1"],
                    top=item["top"],
                    bottom=item["bottom"],
                )
            )

        return result

    # -----------------------------------------------------------------

    def _reconstruct_lines(
        self,
        words: list[Word],
    ) -> list[TextLine]:
        """
        Convert words into logical lines.

        The algorithm groups words by their vertical position
        and reconstructs the original line ordering.
        """

        if not words:
            return []

        groups = self._group_words_by_line(words)

        lines = []

        for group in groups:

            lines.append(
                self._create_text_line(group)
            )

        return lines

    # -----------------------------------------------------------------

    def _group_words_by_line(
        self,
        words: list[Word],
    ) -> list[list[Word]]:
        """
        Group words belonging to the same visual line.

        Returns
        -------
        list[list[Word]]
        """

        #
        # Bucket words by Y coordinate.
        #
        buckets: dict[int, list[Word]] = defaultdict(list)

        for word in words:

            key = round(
                word.top / self.LINE_TOLERANCE
            )

            buckets[key].append(word)

        #
        # Sort buckets vertically.
        #
        ordered = []

        for _, bucket in sorted(
            buckets.items(),
            key=lambda x: x[0],
        ):

            #
            # Sort words left→right.
            #
            bucket.sort(
                key=lambda w: w.x0
            )

            ordered.append(bucket)

        return ordered




    # -----------------------------------------------------------------

    def _create_text_line(
        self,
        page_number: int,
        words: list[Word],
    ) -> TextLine:
        """
        Build one TextLine from a list of Word objects.

        Words are assumed to be sorted from left to right.
        """

        if not words:
            raise ValueError("Cannot create TextLine from empty word list.")

        text = self._join_words(words)

        return TextLine(
            page=page_number,
            words=words,
            text=text,
            top=min(w.top for w in words),
            bottom=max(w.bottom for w in words),
        )

    # -----------------------------------------------------------------

    def _join_words(
        self,
        words: list[Word],
    ) -> str:
        """
        Reconstruct text while preserving spacing.

        pdfplumber returns words without whitespace. We must
        infer spacing from the original X coordinates.

        Example

        Word1.x1 = 100
        Word2.x0 = 108

        gap = 8

        -> insert one space
        """

        if not words:
            return ""

        pieces = [words[0].text]

        previous = words[0]

        for current in words[1:]:

            gap = current.x0 - previous.x1

            #
            # Small gap -> normal single space
            #
            if gap >= self.WORD_GAP:
                pieces.append(" ")

            pieces.append(current.text)

            previous = current

        return "".join(pieces)

    # -----------------------------------------------------------------

    def _assign_page_numbers(
        self,
        page_number: int,
        lines: list[TextLine],
    ) -> None:
        """
        Assign page number to every reconstructed line.
        """

        for line in lines:
            line.page = page_number

    # -----------------------------------------------------------------

    def _sort_lines(
        self,
        lines: list[TextLine],
    ) -> None:
        """
        Ensure lines remain ordered top-to-bottom.

        This is mainly a safety measure.
        """

        lines.sort(
            key=lambda line: (
                line.top,
                line.left,
            )
        )

    # -----------------------------------------------------------------

    def _validate_page(
        self,
        page: Page,
    ) -> None:
        """
        Perform basic consistency checks.
        """

        #
        # Verify ordering.
        #

        previous = -1.0

        for line in page.lines:

            if line.top < previous:

                logger.warning(
                    "Line ordering issue detected on page %d",
                    page.number,
                )

                break

            previous = line.top

    # -----------------------------------------------------------------

    def _finalize_page(
        self,
        page_number: int,
        words: list[Word],
        lines: list[TextLine],
    ) -> Page:
        """
        Complete page construction.
        """

        self._assign_page_numbers(
            page_number,
            lines,
        )

        self._sort_lines(lines)

        page = Page(
            number=page_number,
            words=words,
            lines=lines,
        )

        self._validate_page(page)

        return page


    # -----------------------------------------------------------------

    @staticmethod
    def page_count(
        pages: list[Page],
    ) -> int:

        return len(pages)

    # -----------------------------------------------------------------

    @staticmethod
    def line_count(
        pages: list[Page],
    ) -> int:

        return sum(
            len(page.lines)
            for page in pages
        )

    # -----------------------------------------------------------------

    @staticmethod
    def word_count(
        pages: list[Page],
    ) -> int:

        return sum(
            len(page.words)
            for page in pages
        )
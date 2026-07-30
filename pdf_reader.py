"""
PDF reader.

Reads a Nokia CLI PDF using pdfplumber and converts each page into
Page/Word objects while preserving coordinates.

This module does NOT perform any parsing or cleaning.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterator

import pdfplumber

from models import Page, Word


class PDFReader:
    """
    Reads PDF pages and exposes helper methods for downstream processing.
    """

    #
    # y-coordinate tolerance used while reconstructing lines
    #
    LINE_TOLERANCE = 1.5

    def __init__(self, pdf_file: str | Path):

        self.pdf_file = Path(pdf_file)

        if not self.pdf_file.exists():
            raise FileNotFoundError(self.pdf_file)

    # -----------------------------------------------------

    def pages(self) -> Iterator[Page]:
        """
        Iterate through every page.

        Returns
        -------
        Iterator[Page]
        """

        with pdfplumber.open(self.pdf_file) as pdf:

            for page_number, page in enumerate(pdf.pages, start=1):

                yield Page(
                    number=page_number,
                    words=self._extract_words(page)
                )

    # -----------------------------------------------------

    def _extract_words(self, page) -> list[Word]:

        result = []

        words = page.extract_words(
            keep_blank_chars=False,
            use_text_flow=True,
        )

        for w in words:

            result.append(

                Word(

                    text=w["text"],

                    x0=float(w["x0"]),

                    x1=float(w["x1"]),

                    top=float(w["top"]),

                    bottom=float(w["bottom"]),
                )

            )

        return result

    # -----------------------------------------------------

    def page_to_lines(self, page: Page) -> list[list[Word]]:
        """
        Convert one Page into logical rows.

        Returns
        -------
        list[list[Word]]

        Every inner list represents one line.
        """

        rows = defaultdict(list)

        for word in page.words:

            #
            # Words on same visual row
            #
            key = round(
                word.top / self.LINE_TOLERANCE
            )

            rows[key].append(word)

        result = []

        for _, row in sorted(rows.items()):

            row.sort(
                key=lambda x: x.x0
            )

            result.append(row)

        return result

    # -----------------------------------------------------

    def page_to_text(self, page: Page) -> list[str]:
        """
        Convert Page into reconstructed text lines.

        This preserves the original word ordering.
        """

        lines = []

        for row in self.page_to_lines(page):

            text = " ".join(
                word.text
                for word in row
            )

            lines.append(text)

        return lines
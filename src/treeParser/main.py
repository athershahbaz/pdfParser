"""
main.py

Application entry point for the Nokia Classic CLI parser.
"""

from __future__ import annotations

import sys

from cli import CLI



def main(argv: list[str] | None = None) -> int:
    app = CLI()
    return app.run(argv)


if __name__ == "__main__":
    sys.exit(main())
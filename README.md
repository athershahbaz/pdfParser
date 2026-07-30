# Nokia Classic CLI PDF Parser

## Overview

This project parses Nokia 7250 SR (and other Nokia Classic CLI) Command Reference PDF documents and reconstructs the complete CLI command hierarchy.

The parser analyzes the documentation structure, rebuilds the command tree, validates the resulting hierarchy, and exports it as a nested JSON document.

The generated JSON preserves the hierarchy described in the Nokia documentation.

---

## Features

- Parse Nokia Classic CLI Command Reference PDFs
- Detect command indentation
- Reconstruct complete command trees
- Preserve command ordering
- Validate the generated hierarchy
- Export nested JSON

---

## Project Structure

```
project/

├── config.py
├── models.py
├── pdf_reader.py
├── tokenizer.py
├── parser.py
├── graph.py
├── semantic_analyzer.py
├── validator.py
├── exporter.py
├── cli.py
├── exceptions.py
├── logging_config.py
├── main.py
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.11 or newer
- pdfplumber
- pdfminer.six

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py <input.pdf> <output.json>
```

Example:

```bash
python main.py "7250_SR_OS_Classic_CLI_Command_Reference_Guide.pdf" commands.json
```

Enable verbose logging:

```bash
python main.py input.pdf output.json --verbose
```

---

## Processing Pipeline

```
PDF
 │
 ▼
PDF Reader
 │
 ▼
Tokenizer
 │
 ▼
Parser
 │
 ▼
Semantic Analyzer
 │
 ▼
Validator
 │
 ▼
Exporter
 │
 ▼
JSON
```

---

## Example Output

For a command hierarchy:

```
configure
    router
        interface
            address
```

The generated JSON is:

```json
{
    "configure": [
        {
            "router": [
                {
                    "interface": [
                        {
                            "address": []
                        }
                    ]
                }
            ]
        }
    ]
}
```

---

## Error Handling

The application reports errors for situations such as:

- Invalid PDF
- Corrupt PDF
- Parsing failures
- Invalid command hierarchy
- Validation failures
- Export failures

Errors are written to the console through the logging system.

---

## Limitations

The parser is designed specifically for Nokia Classic CLI Command Reference manuals that follow the standard documentation structure.

It is not intended to parse arbitrary PDF documents.

---

## License

This project is intended for internal engineering and automation use.
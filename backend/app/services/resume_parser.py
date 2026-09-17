from pathlib import Path

import pymupdf as fitz


def extract_text(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz).

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with fitz.open(str(path)) as document:
        text = "".join(page.get_text() for page in document)

    return text.strip()
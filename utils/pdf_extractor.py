"""PDF text extraction using PyMuPDF (fitz)."""

import re
from typing import Optional
import fitz  # PyMuPDF


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract plain text from a Streamlit UploadedFile (PDF).

    Args:
        uploaded_file: A Streamlit UploadedFile object with a .read() method.

    Returns:
        A single string containing all extracted text, pages joined by newlines.
    """
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())

    doc.close()
    return "\n".join(pages_text)


def extract_screenplay_text(uploaded_file) -> tuple[Optional[str], Optional[dict]]:
    """
    Extract and clean text from a screenplay PDF.

    Args:
        uploaded_file: A Streamlit UploadedFile object.

    Returns:
        A tuple of (cleaned_text, metadata) where:
          - cleaned_text is the full cleaned screenplay string, or None on failure.
          - metadata is a dict with 'page_count' and 'word_count', or None on failure.
    """
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = doc.page_count

        raw_pages = []
        for page in doc:
            raw_pages.append(page.get_text())
        doc.close()

        raw_text = "\n".join(raw_pages)
        cleaned = _clean_text(raw_text)

        if not cleaned:
            return None, None

        word_count = len(cleaned.split())
        metadata = {"page_count": page_count, "word_count": word_count}
        return cleaned, metadata

    except Exception:
        return None, None


def get_screenplay_preview(text: str, num_lines: int = 20) -> str:
    """
    Return the first `num_lines` non-empty lines of the screenplay as a preview.

    Args:
        text: The full cleaned screenplay text.
        num_lines: Number of lines to include in the preview (default 20).

    Returns:
        A string containing the first `num_lines` lines joined by newlines.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    preview_lines = lines[:num_lines]
    return "\n".join(preview_lines)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """
    Clean raw PDF-extracted text for LLM consumption.

    Steps:
      1. Normalise Windows-style line endings to Unix.
      2. Replace form-feed characters (page breaks) with a blank line.
      3. Collapse runs of more than two consecutive blank lines into two.
      4. Strip leading/trailing whitespace from each line while preserving
         screenplay indentation structure (tabs / multiple spaces kept intact).
      5. Strip leading/trailing whitespace from the full string.
    """
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace form feeds with a blank line separator
    text = text.replace("\f", "\n\n")

    # Strip trailing whitespace from each line (keep leading for indentation)
    lines = [line.rstrip() for line in text.splitlines()]

    # Collapse 3+ consecutive blank lines into 2
    cleaned_lines: list[str] = []
    blank_run = 0
    for line in lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                cleaned_lines.append("")
        else:
            blank_run = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()

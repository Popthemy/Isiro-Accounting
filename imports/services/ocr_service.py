"""OCR service — wrapper around pytesseract for scanned PDFs.

Tesseract is optional in this environment.  If the binary is not installed
the service degrades gracefully and returns an empty result so the caller
can show a helpful message.
"""

from __future__ import annotations

import io


def ocr_pdf_to_text(file) -> str:
    """Convert a scanned PDF to raw text via pytesseract + pdfplumber.

    Returns an empty string if Tesseract is unavailable.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_bytes  # type: ignore
    except ImportError:
        return ""

    try:
        content = file.read()
        file.seek(0)
        images = convert_from_bytes(content)
        text_parts: list[str] = []
        for img in images:
            text_parts.append(pytesseract.image_to_string(img))
        return "\n".join(text_parts)
    except Exception:
        return ""

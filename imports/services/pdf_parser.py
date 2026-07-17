"""PDF parser using pdfplumber with OCR fallback via pytesseract."""

from __future__ import annotations

import io
from decimal import Decimal, InvalidOperation

import pdfplumber

from .column_mapping import map_columns, find_header_row


def parse_pdf_file(file) -> list[dict]:
    """Extract transactions from a PDF bank statement.

    Strategy:
    1. Use pdfplumber to extract tables (most statements have them).
    2. If no tables found, fall back to OCR text extraction.
    """
    content = file.read()
    file.seek(0)

    rows: list[dict] = []
    try:
        rows = _extract_from_tables(content)
    except Exception:
        pass

    if not rows:
        try:
            rows = _extract_from_text(content)
        except Exception:
            pass

    return rows


def _extract_from_tables(content: bytes) -> list[dict]:
    """Extract rows from PDF tables using pdfplumber."""
    rows: list[dict] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue

                table_rows = [
                    [str(cell or "").strip() for cell in row] for row in table
                ]

                header_index, header_row = find_header_row(table_rows)

                if header_index is None:
                    continue
            
                # headers = [str(h or "").strip() for h in table[0]]
                # print(f"Extracted headers: {headers}")  # Debugging line
                mapping = map_columns(header_row)

                if "date" not in mapping or "amount" not in mapping:
                    continue

                for record in table_rows[header_index + 1:]:
                    parsed = _parse_record(record, mapping)
                    if parsed:
                        rows.append(parsed)
    return rows


def _extract_from_text(content: bytes) -> list[dict]:
    """Fallback: extract lines of text and try to find date/amount patterns."""
    import re

    rows: list[dict] = []
    date_re = re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")
    amount_re = re.compile(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+\.\d{2})")

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                date_match = date_re.search(line)
                amounts = amount_re.findall(line)
                if date_match and amounts:
                    date_val = date_match.group(1)
                    amount_str = amounts[-1].replace(",", "")
                    try:
                        amount = abs(Decimal(amount_str))
                    except InvalidOperation:
                        continue
                    description = line.replace(date_match.group(0), "").strip()
                    for a in amounts:
                        description = description.replace(a, "").strip()
                    rows.append({
                        "date": date_val,
                        "description": description[:200],
                        "amount": str(amount),
                        "transaction_type": "expense",
                        "category": "",
                    })
    return rows


def _parse_record(record: list, mapping: dict) -> dict | None:
    """Parse a single table row using the column mapping."""
    try:
        date_val = str(record[mapping["date"]] or "").strip()
        if not date_val:
            return None

        desc_val = ""
        if "description" in mapping and mapping["description"] < len(record):
            desc_val = str(record[mapping["description"]] or "").strip()

        txn_type = "expense"
        if "debit" in mapping and "credit" in mapping:
            debit_raw = record[mapping["debit"]] if mapping["debit"] < len(record) else None
            credit_raw = record[mapping["credit"]] if mapping["credit"] < len(record) else None
            credit_val = _to_decimal(credit_raw)
            debit_val = _to_decimal(debit_raw)
            if credit_val and credit_val > 0:
                amount = credit_val
                txn_type = "income"
            elif debit_val and debit_val > 0:
                amount = debit_val
                txn_type = "expense"
            else:
                return None
        else:
            raw = record[mapping["amount"]] if mapping["amount"] < len(record) else None
            amount = _to_decimal(raw)
            if amount is None or amount == 0:
                return None

        return {
            "date": date_val,
            "description": desc_val[:200],
            "amount": str(amount),
            "transaction_type": txn_type,
            "category": "",
        }
    except Exception:
        return None


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    s = str(value).strip().replace(",", "").replace(" ", "")
    if not s:
        return None
    try:
        return abs(Decimal(s))
    except InvalidOperation:
        return None

"""CSV parser using pandas with smart column mapping."""

from __future__ import annotations

import io
from decimal import Decimal, InvalidOperation

import pandas as pd

from .column_mapping import map_columns


def parse_csv_file(file) -> list[dict]:
    """Parse an uploaded CSV file and return a list of normalised rows.

    Each row is a dict with keys: ``date``, ``description``, ``amount``,
    ``transaction_type``.
    """
    # Read the file into a DataFrame.
    content = file.read()
    file.seek(0)

    # Try comma first, then semicolon and tab.
    for sep in [",", ";", "\t"]:
        try:
            df = pd.read_csv(io.BytesIO(content), sep=sep, dtype=str)
            if len(df.columns) > 1:
                break
        except Exception:
            continue

    headers = list(df.columns)
    mapping = map_columns(headers)

    rows: list[dict] = []
    if "date" not in mapping or "amount" not in mapping:
        return rows

    for _, record in df.iterrows():
        try:
            date_val = str(record.iloc[mapping["date"]]).strip()
            if not date_val or date_val.lower() == "nan":
                continue

            desc_val = ""
            if "description" in mapping:
                desc_val = str(record.iloc[mapping["description"]]).strip()
                if desc_val.lower() == "nan":
                    desc_val = ""

            # Determine amount and transaction type.
            txn_type = "expense"
            if "debit" in mapping and "credit" in mapping:
                debit_raw = record.iloc[mapping["debit"]]
                credit_raw = record.iloc[mapping["credit"]]
                debit_val = _to_decimal(debit_raw)
                credit_val = _to_decimal(credit_raw)
                if credit_val and credit_val > 0:
                    amount = credit_val
                    txn_type = "income"
                elif debit_val and debit_val > 0:
                    amount = debit_val
                    txn_type = "expense"
                else:
                    continue
            else:
                raw = record.iloc[mapping["amount"]]
                amount = _to_decimal(raw)
                if amount is None or amount == 0:
                    continue
                if amount < 0:
                    amount = abs(amount)
                    txn_type = "expense"
                else:
                    # Heuristic: amounts in a "debit" column are expenses.
                    header = str(headers[mapping["amount"]]).lower()
                    if "debit" in header or "withdrawal" in header:
                        txn_type = "expense"
                    elif "credit" in header or "deposit" in header:
                        txn_type = "income"

            rows.append({
                "date": date_val,
                "description": desc_val,
                "amount": str(amount),
                "transaction_type": txn_type,
                "category": "",
            })
        except Exception:
            continue

    return rows


def _to_decimal(value) -> Decimal | None:
    """Convert a messy string value to Decimal, handling commas and spaces."""
    if value is None:
        return None
    s = str(value).strip().replace(",", "")
    if not s or s.lower() == "nan":
        return None
    try:
        return abs(Decimal(s))
    except InvalidOperation:
        return None

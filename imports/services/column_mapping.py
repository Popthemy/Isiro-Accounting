"""Smart bank-statement column mapping.

Different banks use different header names for the same logical column.
This module normalises headers and maps them to internal field names using
synonym arrays, so the parser can auto-detect columns from any bank.
"""

import re

# ---------------------------------------------------------------------------
# Synonym dictionaries — each list contains alternative header names that
# banks around the world use for the same logical field.
# ---------------------------------------------------------------------------

DATE_FIELDS = [
    "date", "transactiondate", "postingdate", "valuedate",
    "transdate", "trxdate", "trxndate", "operationdate",
    "entrydate", "bookdate", "processdate",
]

DESCRIPTION_FIELDS = [
    "description", "narration", "details", "transactiondetail", "transactiondetails",
    "remarks", "memo", "particulars", "transactiondescription",
    "transactionnarration", "detailsnarration", "payee",
    "beneficiary", "reference", "transactionref",
]

AMOUNT_FIELDS = [
    "amount", "transactionamount", "debit", "credit",
    "value", "transactionvalue", "amountusd", "amountlocal",
    "withdrawal", "deposit", "outgoing", "incoming", "moneyin", "moneyout", "paidin", "paidout",
]

BALANCE_FIELDS = [
    "balance", "availablebalance", "closingbalance",
    "runningbalance", "ledgerbalance", "balanceafter",
    "currentbalance", "totalmoneyin"
]

# Fields that, when present, indicate a debit vs credit.
DEBIT_FIELDS = ["debit", "withdrawal", "outgoing", "paidout", "moneyout"]
CREDIT_FIELDS = ["credit", "deposit", "incoming", "paidin", "moneyin"]

# Header
ALL_HEADER_FIELDS = (
    set(DATE_FIELDS) | set(DESCRIPTION_FIELDS) | set(
        AMOUNT_FIELDS) | {"transactionid", "reference", "rrn"}
)


def normalise_header(header: str) -> str:
    """Lowercase, strip spaces and special characters from a header."""
    if not header:
        return ""
    h = header.strip().lower()
    h = re.sub(r"[^a-z0-9]", "", h)  # remove spaces, underscores, hyphens
    return h


def header_score(row):
    found = {
        "date": False,
        "description": False,
        "amount": False,
        "balance": False,
        "reference": False,
    }

    for cell in row:
        norm = normalise_header(cell)

        if _match(norm, DATE_FIELDS):
            found["date"] = True
        elif _match(norm, DESCRIPTION_FIELDS):
            found["description"] = True
        elif _match(norm, AMOUNT_FIELDS):
            found["amount"] = True
        elif _match(norm, BALANCE_FIELDS):
            found["balance"] = True
        elif norm in {"transactionid", "reference", "rrn"}:
            found["reference"] = True

    return sum(found.values())


def find_header_row(rows, min_score=3):
    best_row = None
    best_index = None
    best_score = 0

    for i, row in enumerate(rows):
        score = header_score(row)

        if score > best_score:
            best_score = score
            best_row = row
            best_index = i

    if best_score >= min_score:
        return best_index, best_row

    return None, None


def _match(normalised: str, synonyms: list[str]) -> bool:
    """Return True if *normalised* matches any synonym (exact or contains)."""
    for syn in synonyms:
        if normalised == syn or syn in normalised:
            return True
    return False


def map_columns(headers: list[str]) -> dict:
    """Map a list of raw bank headers to internal field names.

    Returns a dict like::

        {"date": 0, "description": 1, "amount": 2, "balance": 3}

    where keys are internal names and values are column indices.
    """
    mapping: dict[str, int] = {}
    debit_idx: int | None = None
    credit_idx: int | None = None

    for idx, raw in enumerate(headers):
        norm = normalise_header(raw)
        
        print(f"Normalised header '{raw}' to '{norm}'")  # Debugging line
        if not norm:
            continue

        if "date" not in mapping and _match(norm, DATE_FIELDS):
            mapping["date"] = idx
        elif "description" not in mapping and _match(norm, DESCRIPTION_FIELDS):
            mapping["description"] = idx
        elif "balance" not in mapping and _match(norm, BALANCE_FIELDS):
            mapping["balance"] = idx
        elif _match(norm, AMOUNT_FIELDS):
            # Prefer a single generic "amount" column, but remember
            # separate debit/credit columns for later type detection.
            if _match(norm, DEBIT_FIELDS):
                debit_idx = idx
            elif _match(norm, CREDIT_FIELDS):
                credit_idx = idx
            elif "amount" not in mapping:
                mapping["amount"] = idx

    # If we found separate debit/credit columns, store both.
    if debit_idx is not None and credit_idx is not None:
        mapping["debit"] = debit_idx
        mapping["credit"] = credit_idx
        # Use debit as the primary amount if no generic amount was found.
        if "amount" not in mapping:
            mapping["amount"] = debit_idx
    elif debit_idx is not None:
        mapping["amount"] = debit_idx
    elif credit_idx is not None:
        mapping["amount"] = credit_idx

    return mapping

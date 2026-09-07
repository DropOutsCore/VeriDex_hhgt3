"""Deterministic Canonical JSON Serialization & SHA-256 Hashing Utilities.

==================================================
CANONICALIZATION ARCHITECTURE
==================================================

To generate a reproducible cryptographic fingerprint (EVIDENCE DNA) for a verification event:
1. All dictionary keys must be sorted deterministically in ascending lexicographical order (`sort_keys=True`).
2. Structural whitespace, indentations, and trailing spaces must be eliminated (`separators=(',', ':')`).
3. Floating-point metrics must be rounded deterministically (e.g., to 4 decimal places).
4. Non-ASCII characters must be encoded consistently (`ensure_ascii=True`).
5. Datetime objects and UUIDs must be serialized into standardized ISO 8601 strings.

The resulting canonical JSON byte string is fed into SHA-256 to produce the VERIDEX Evidence Hash.
"""

import hashlib
import json
from datetime import datetime, date
from uuid import UUID
from typing import Any, Union, Dict
from pydantic import BaseModel


def _normalize_obj(obj: Any, float_precision: int = 4) -> Any:
    """Recursively normalize data structure into canonical JSON-serializable primitives."""
    if isinstance(obj, BaseModel):
        obj = obj.model_dump()

    if isinstance(obj, dict):
        return {
            str(k): _normalize_obj(v, float_precision)
            for k, v in sorted(obj.items(), key=lambda item: str(item[0]))
        }

    if isinstance(obj, (list, tuple)):
        return [_normalize_obj(item, float_precision) for item in obj]

    if isinstance(obj, float):
        return round(obj, float_precision)

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, UUID):
        return str(obj)

    return obj


def canonicalize_json(data: Any, float_precision: int = 4) -> str:
    """Serialize any input data structure into a deterministic canonical JSON string.

    Args:
        data: Dict, list, Pydantic model, or primitive payload.
        float_precision: Decimal places for float normalization (default: 4).

    Returns:
        Deterministic canonical JSON string.
    """
    normalized = _normalize_obj(data, float_precision=float_precision)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def canonicalize_bytes(data: Any, float_precision: int = 4) -> bytes:
    """Serialize data into deterministic canonical UTF-8 encoded JSON bytes."""
    return canonicalize_json(data, float_precision=float_precision).encode("utf-8")


def canonical_sha256(data: Any, float_precision: int = 4) -> str:
    """Calculate cryptographic SHA-256 hex fingerprint over canonicalized JSON representation.

    Args:
        data: Data structure to canonicalize and hash.
        float_precision: Decimal places for float normalization.

    Returns:
        64-character lowercase hexadecimal SHA-256 digest string.
    """
    json_bytes = canonicalize_bytes(data, float_precision=float_precision)
    return hashlib.sha256(json_bytes).hexdigest()

"""
Regulation update and import utilities for Adhi Compliance.

Provides:
  - check_for_updates()                   — placeholder for external feed polling
  - import_regulations_from_file(path)    — parse JSON/CSV files of regulations
  - update_regulation(reg_id, updates, db) — update DB record and re-embed

These functions are called from admin API routes and can also be wired to
scheduled Celery tasks.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.store.models import Regulation

logger = logging.getLogger("adhi_compliance.regulation_updater")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_for_updates() -> List[Dict[str, Any]]:
    """
    Check external regulatory feeds for new or updated regulations.

    Currently a placeholder — returns an empty list.
    Future implementation should poll sources such as:
      - EUR-Lex (https://eur-lex.europa.eu/SPARQL)
      - Federal Register API (https://www.federalregister.gov/api/v1)
      - FCA RegData (UK)

    Returns:
        A list of dicts describing available updates (could be empty).
    """
    logger.info("check_for_updates called (placeholder — no external feed configured)")
    return []


def import_regulations_from_file(file_path: str, db: Session) -> List[Regulation]:
    """
    Parse a JSON or CSV file of regulations and persist them to the database.

    JSON format (array of objects):
        [{"name": "...", "jurisdiction": "EU", "category": "AI Governance", ...}, ...]

    CSV format (header row required):
        name,short_name,jurisdiction,category,effective_date,enforcement_date,full_text,url

    Args:
        file_path: Absolute or relative path to the input file.
        db:        Active SQLAlchemy session.

    Returns:
        List of newly created Regulation ORM instances.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Regulation file not found: {file_path}")

    raw_bytes = path.read_bytes()
    suffix = path.suffix.lower()

    if suffix == ".json":
        records = _parse_json(raw_bytes)
    elif suffix == ".csv":
        records = _parse_csv(raw_bytes)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .json or .csv")

    created: List[Regulation] = []
    for rec in records:
        reg = _build_regulation(rec)
        db.add(reg)
        created.append(reg)

    db.commit()
    for reg in created:
        db.refresh(reg)

    logger.info("Imported %d regulations from %s", len(created), file_path)
    return created


def import_regulations_from_bytes(
    content: bytes,
    file_type: str,
    db: Session,
) -> List[Regulation]:
    """
    Parse regulation records from raw bytes (used for HTTP file upload).

    Args:
        content:   Raw file bytes.
        file_type: "json" or "csv".
        db:        Active SQLAlchemy session.

    Returns:
        List of newly created Regulation ORM instances.
    """
    if file_type == "json":
        records = _parse_json(content)
    elif file_type == "csv":
        records = _parse_csv(content)
    else:
        raise ValueError(f"Unsupported file_type: {file_type}")

    created: List[Regulation] = []
    for rec in records:
        reg = _build_regulation(rec)
        db.add(reg)
        created.append(reg)

    db.commit()
    for reg in created:
        db.refresh(reg)

    logger.info("Imported %d regulations from bytes (%s)", len(created), file_type)
    return created


def update_regulation(
    reg_id: str,
    updates: Dict[str, Any],
    db: Session,
    re_embed: bool = False,
) -> Optional[Regulation]:
    """
    Update a Regulation record and optionally re-embed it in the vector index.

    Args:
        reg_id:   Primary key of the regulation.
        updates:  Dict of fields to update (partial update).
        db:       Active SQLAlchemy session.
        re_embed: If True, trigger re-embedding of the updated regulation text.

    Returns:
        The updated Regulation, or None if not found.
    """
    regulation = db.query(Regulation).filter(
        Regulation.id == reg_id,
        Regulation.is_deleted == False,
    ).first()

    if not regulation:
        return None

    for field, value in updates.items():
        if hasattr(regulation, field):
            setattr(regulation, field, value)

    db.commit()
    db.refresh(regulation)

    if re_embed and regulation.full_text:
        _re_embed_regulation(regulation)

    return regulation


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_json(content: bytes) -> List[Dict[str, Any]]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("JSON must be an array of regulation objects or a single object.")
    return data


def _parse_csv(content: bytes) -> List[Dict[str, Any]]:
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty or has no data rows.")
    return rows


_DATE_FIELDS = {"effective_date", "enforcement_date"}


def _build_regulation(rec: Dict[str, Any]) -> Regulation:
    """Convert a parsed dict into a Regulation ORM instance."""
    import uuid

    data: Dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "name": rec.get("name", "Unnamed Regulation"),
        "short_name": rec.get("short_name") or None,
        "jurisdiction": rec.get("jurisdiction") or None,
        "category": rec.get("category") or None,
        "full_text": rec.get("full_text") or rec.get("text") or None,
        "url": rec.get("url") or None,
        "is_deleted": False,
    }

    for field in _DATE_FIELDS:
        raw = rec.get(field)
        if raw:
            try:
                data[field] = datetime.fromisoformat(str(raw))
            except (ValueError, TypeError):
                data[field] = None
        else:
            data[field] = None

    return Regulation(**data)


def _re_embed_regulation(regulation: Regulation) -> None:
    """Trigger re-embedding of a single regulation into the FAISS index."""
    try:
        from app.services.regulation_embedder import embed_all_regulations  # type: ignore
        # Re-embed everything (simple strategy; optimize per-doc if index grows large)
        embed_all_regulations()
        logger.info("Re-embedded regulation %s (%s)", regulation.id, regulation.short_name)
    except Exception as exc:
        logger.warning("Re-embedding failed for regulation %s: %s", regulation.id, exc)

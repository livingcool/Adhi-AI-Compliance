"""
Compliance Checker Service.

Performs RAG-based compliance analysis for an AI system against a specific
regulation using the regulation FAISS index and Gemini LLM.
"""

import json
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from google import genai
from google.genai import types as genai_types
from sqlalchemy.orm import Session

logger = logging.getLogger("adhi.compliance_checker")

from app.config import get_settings
from app.store.models import AISystem, ComplianceCheck, Regulation
from app.services.regulation_embedder import get_regulation_embedder

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

COMPLIANCE_CHECK_TEMPLATE = """You are an expert AI compliance analyst. Assess whether the AI system described below complies with the specified regulation based on the provided regulation excerpts.

## AI System Profile
- Name: {system_name}
- Purpose: {purpose}
- Description: {description}
- Data Types Processed: {data_types}
- Deployment Regions: {deployment_regions}
- Risk Classification: {risk_classification}

## Regulation Being Assessed
{regulation_name} ({regulation_short_name}) — Jurisdiction: {jurisdiction}

## Relevant Regulation Excerpts (RAG Retrieved)
{regulation_context}

## Task
Based on the regulation excerpts above, assess compliance for this AI system.

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{{
  "status": "<compliant|non_compliant|partial>",
  "gap_description": "<describe specific compliance gaps, or 'No significant gaps identified' if compliant>",
  "remediation_steps": "<numbered list of concrete actions to achieve/maintain compliance, or 'N/A' if fully compliant>",
  "priority": "<critical|high|medium|low>",
  "deadline_days": <integer number of days from today to recommended deadline, e.g. 30, 60, 90, 180>
}}

Priority guide:
- critical: Prohibited practices or imminent enforcement
- high: Major gaps in high-risk system requirements
- medium: Partial compliance, gaps addressable within 90 days
- low: Minor documentation or process gaps
"""

# Number of regulation chunks to retrieve for context
_TOP_K_CHUNKS = 6


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_system_profile_query(system: AISystem, regulation: Regulation) -> str:
    """
    Build a natural-language query representing the system + regulation
    combination for vector retrieval.
    """
    parts = [
        f"compliance requirements for {system.purpose or system.name}",
        f"{regulation.short_name or regulation.name} obligations",
    ]
    if system.data_types:
        parts.append(f"data types: {', '.join(system.data_types)}")
    if system.deployment_regions:
        parts.append(f"jurisdiction: {', '.join(system.deployment_regions)}")
    return " ".join(parts)


def _format_chunks_as_context(chunks: list) -> str:
    """Format retrieved regulation chunks into a readable context block."""
    if not chunks:
        return "No relevant regulation excerpts found in the knowledge base."
    sections = []
    for i, chunk in enumerate(chunks, 1):
        score = chunk.get("score", 0)
        short = chunk.get("short_name") or chunk.get("regulation_name", "")
        text = chunk.get("text", "")
        sections.append(f"[Excerpt {i} – {short} | relevance: {score:.2f}]\n{text}")
    return "\n\n---\n\n".join(sections)


def _call_gemini(prompt: str) -> Dict[str, Any]:
    """
    Call Gemini to generate a compliance assessment.
    Returns a parsed dict with the expected keys.
    Raises RuntimeError on unrecoverable failures.
    """
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured.")

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1024,
        ),
    )
    raw = response.text.strip()

    # Strip markdown code fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


def _deadline_from_days(days: Any) -> Optional[datetime]:
    """Convert a days integer (possibly from LLM JSON) into a datetime."""
    try:
        return datetime.utcnow() + timedelta(days=int(days))
    except (TypeError, ValueError):
        return datetime.utcnow() + timedelta(days=90)  # sensible default


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_compliance(
    ai_system_id: str,
    regulation_id: str,
    org_id: str,
    db: Session,
) -> ComplianceCheck:
    """
    Run a RAG-based compliance check for an AI system against a regulation.

    Workflow:
    1. Fetch AISystem and Regulation from DB.
    2. Build a semantic query from the system profile.
    3. Retrieve the top-K most relevant regulation chunks.
    4. Send a structured prompt to Gemini for compliance assessment.
    5. Persist and return a ComplianceCheck record.

    Args:
        ai_system_id:  ID of the AISystem to assess.
        regulation_id: ID of the Regulation to check against.
        org_id:        Organisation ID for the record.
        db:            SQLAlchemy Session.

    Returns:
        A persisted ComplianceCheck ORM object.

    Raises:
        ValueError: if the system or regulation is not found.
        RuntimeError: if the LLM call fails.
    """
    # 1. Fetch entities
    system = db.query(AISystem).filter(AISystem.id == ai_system_id).first()
    if not system:
        raise ValueError(f"AISystem '{ai_system_id}' not found.")

    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise ValueError(f"Regulation '{regulation_id}' not found.")

    # 2. Retrieve relevant regulation chunks
    embedder = get_regulation_embedder()
    query = _build_system_profile_query(system, regulation)
    chunks = embedder.search(
        query=query,
        top_k=_TOP_K_CHUNKS,
        regulation_id_filter=regulation_id,
    )

    # Fall back to unfiltered search if no chunks for this specific regulation
    if not chunks:
        chunks = embedder.search(
            query=query,
            top_k=_TOP_K_CHUNKS,
            jurisdiction_filter=regulation.jurisdiction,
        )

    # 3. Build prompt
    regulation_context = _format_chunks_as_context(chunks)
    prompt = COMPLIANCE_CHECK_TEMPLATE.format(
        system_name=system.name,
        purpose=system.purpose or "N/A",
        description=system.description or "N/A",
        data_types=", ".join(system.data_types or []) or "N/A",
        deployment_regions=", ".join(system.deployment_regions or []) or "N/A",
        risk_classification=system.risk_classification or "unclassified",
        regulation_name=regulation.name,
        regulation_short_name=regulation.short_name or regulation.name,
        jurisdiction=regulation.jurisdiction or "N/A",
        regulation_context=regulation_context,
    )

    # 4. Call LLM
    try:
        result = _call_gemini(prompt)
    except Exception as exc:
        logger.error("llm_compliance_check_failed", extra={"error": str(exc)})
        result = {
            "status": "pending",
            "gap_description": f"Automated check failed: {exc}. Manual review required.",
            "remediation_steps": "Review regulation manually and reassess.",
            "priority": "medium",
            "deadline_days": 90,
        }

    # Validate/normalise status
    valid_statuses = {"compliant", "non_compliant", "partial", "pending"}
    status = result.get("status", "pending")
    if status not in valid_statuses:
        status = "pending"

    valid_priorities = {"critical", "high", "medium", "low"}
    priority = result.get("priority", "medium")
    if priority not in valid_priorities:
        priority = "medium"

    deadline = _deadline_from_days(result.get("deadline_days", 90))

    # 5. Persist ComplianceCheck
    check = ComplianceCheck(
        id=str(uuid.uuid4()),
        ai_system_id=ai_system_id,
        regulation_id=regulation_id,
        status=status,
        gap_description=result.get("gap_description"),
        remediation_steps=result.get("remediation_steps"),
        priority=priority,
        deadline=deadline,
        org_id=org_id,
        checked_at=datetime.utcnow(),
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    logger.info(
        "compliance_check_complete",
        extra={
            "system": system.name,
            "regulation": regulation.short_name,
            "status": status,
            "priority": priority,
        },
    )
    return check

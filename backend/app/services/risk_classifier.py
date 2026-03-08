"""
Risk Classifier Service.

Classifies AI systems against EU AI Act Annex III risk categories using a
rule-based approach with optional Gemini LLM refinement for uncertain cases.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types as genai_types
from sqlalchemy.orm import Session

logger = logging.getLogger("adhi.risk_classifier")

from app.config import get_settings
from app.store.models import AISystem, Regulation

# ---------------------------------------------------------------------------
# EU AI Act Annex III risk rules
# Each rule: (keywords_in_any_field, risk_tier, reason_label)
# Keywords are checked (case-insensitive) against: purpose, description,
# data_types joined as a string.
# ---------------------------------------------------------------------------

_UNACCEPTABLE_RULES: List[Tuple[List[str], str]] = [
    (["social scor", "social credit", "social rating"], "Social scoring system"),
    (["subliminal", "subconscious manipulat", "unconscious manipulat", "manipulative technique"], "Subliminal/manipulative AI technique"),
    (["exploit vulnerab", "exploit disab", "exploit elderly", "exploit children"], "Exploitation of vulnerable groups"),
    (["biometric categoris", "biometric categor", "categorise by race", "categorise by religion",
      "categorise by political", "categorise by sexual"], "Prohibited biometric categorisation"),
    (["untargeted scraping facial", "scrape facial image", "facial recognition database", "mass facial scraping"], "Mass facial image scraping"),
]

_HIGH_RISK_RULES: List[Tuple[List[str], str]] = [
    # Biometric identification
    (["biometric identif", "facial recognit", "fingerprint identif", "iris recognit",
      "voice identif", "biometric", "liveness detect"], "Biometric identification system (Annex III §1)"),
    # Critical infrastructure
    (["critical infrastructure", "power grid", "water supply", "transport network",
      "energy grid", "utility management", "pipeline", "critical system"], "Critical infrastructure management (Annex III §2)"),
    # Education / vocational
    (["education", "academic", "student assessment", "student evaluat", "exam", "admission",
      "vocational training", "learning outcome", "school", "university", "grading"], "Education/vocational assessment (Annex III §3)"),
    # Employment / hiring
    (["hiring", "recruitment", "job applicant", "employee evaluat", "worker monitor",
      "performance review", "applicant screen", "cv screen", "resume screen",
      "interview", "employment decision", "HR decision", "workforce"], "Employment/hiring decisions (Annex III §4)"),
    # Essential services
    (["credit scor", "loan", "insurance", "benefit", "social welfare", "public service",
      "essential service", "health insurance", "creditworthiness"], "Essential services access (Annex III §5)"),
    # Law enforcement
    (["law enforcement", "police", "crime predict", "criminal", "evidence assess",
      "risk profile", "profiling", "investigation", "court", "judicial", "prosecution"], "Law enforcement (Annex III §6)"),
    # Immigration / border
    (["immigration", "border control", "asylum", "visa", "passport", "migration",
      "border management"], "Immigration/border management (Annex III §7)"),
    # Justice / democratic
    (["justice", "democratic process", "election", "voting", "court decision",
      "legal ruling", "judicial decision", "political campaign"], "Justice/democratic processes (Annex III §8)"),
]

_LIMITED_RISK_RULES: List[Tuple[List[str], str]] = [
    (["deepfake", "synthetic media", "synthetic video", "synthetic audio",
      "synthetic image", "voice clone", "voice synthesis", "ai-generated content",
      "ai generated content", "generated content", "synthetic face"], "AI-generated content / deepfakes (transparency required)"),
    (["chatbot", "virtual assistant", "conversational ai", "chat assistant",
      "dialogue system", "customer service bot", "support bot"], "Chatbot / conversational AI (transparency required)"),
    (["emotion recognit", "sentiment detection", "mood detect", "affect recognit",
      "emotional state", "emotion detect"], "Emotion recognition (transparency required)"),
]

# Confidence threshold: if rule-based is "unclassified" or we have no strong
# keyword match, we fall back to LLM.
_LLM_CLASSIFY_PROMPT = """You are an expert EU AI Act compliance analyst.

Classify the following AI system according to EU AI Act risk categories.

AI System Profile:
- Name: {name}
- Purpose: {purpose}
- Description: {description}
- Data Types: {data_types}
- Deployment Regions: {deployment_regions}

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{{
  "risk_tier": "<unacceptable|high|limited|minimal>",
  "confidence": "<high|medium|low>",
  "reasoning": "<1-2 sentence explanation referencing specific EU AI Act provisions>",
  "eu_act_category": "<relevant Annex III category or Article 5 provision, or 'N/A'>"
}}"""


def _build_search_text(system: AISystem) -> str:
    """Combine searchable text fields into one string for keyword matching."""
    parts = [
        system.purpose or "",
        system.description or "",
        system.name or "",
        " ".join(system.data_types or []),
    ]
    return " ".join(parts).lower()


def _rule_based_classify(search_text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (risk_tier, reasoning) if a rule matches, else (None, None).
    Checks in priority order: unacceptable → high → limited.
    """
    for keywords, reason in _UNACCEPTABLE_RULES:
        if any(kw in search_text for kw in keywords):
            return "unacceptable", reason

    for keywords, reason in _HIGH_RISK_RULES:
        if any(kw in search_text for kw in keywords):
            return "high", reason

    for keywords, reason in _LIMITED_RISK_RULES:
        if any(kw in search_text for kw in keywords):
            return "limited", reason

    return None, None


def _llm_classify(system: AISystem) -> Tuple[str, str]:
    """
    Call Gemini to classify the system when rule-based is uncertain.
    Returns (risk_tier, reasoning). Defaults to 'minimal' on error.
    """
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        return "minimal", "LLM unavailable (no GOOGLE_API_KEY); defaulting to minimal risk."

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)

        prompt = _LLM_CLASSIFY_PROMPT.format(
            name=system.name or "N/A",
            purpose=system.purpose or "N/A",
            description=system.description or "N/A",
            data_types=", ".join(system.data_types or []) or "N/A",
            deployment_regions=", ".join(system.deployment_regions or []) or "N/A",
        )

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=512,
            ),
        )
        raw = response.text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)
        tier = parsed.get("risk_tier", "minimal")
        reasoning = parsed.get("reasoning", "LLM classification.")
        if tier not in ("unacceptable", "high", "limited", "minimal"):
            tier = "minimal"
        return tier, reasoning

    except Exception as e:
        logger.error("llm_classify_failed", extra={"error": str(e)})
        return "minimal", f"LLM classification failed ({type(e).__name__}); defaulting to minimal risk."


def _get_applicable_regulations(
    db: Session,
    risk_tier: str,
    deployment_regions: List[str],
) -> List[Dict[str, Any]]:
    """
    Query the DB for regulations relevant to the given risk tier and regions.

    Mapping logic:
    - unacceptable → EU AI Act Art. 5 (prohibited practices)
    - high         → All regulations matching the deployment jurisdictions
    - limited      → Transparency-related regulations in matching jurisdictions
    - minimal      → No specific mandatory regulations
    """
    if not deployment_regions:
        deployment_regions = []

    # Normalise regions to uppercase
    regions = [r.upper() for r in deployment_regions]

    q = db.query(Regulation)

    if risk_tier == "unacceptable":
        # Specifically Art. 5 (prohibited)
        regs = q.filter(
            Regulation.jurisdiction == "EU"
        ).filter(
            Regulation.short_name.like("%Art. 5%")
        ).all()
        if not regs:
            # Fall back to all EU AI Act entries
            regs = q.filter(Regulation.jurisdiction == "EU").all()

    elif risk_tier == "high":
        # All regulations for matching regions
        if regions:
            regs = q.filter(Regulation.jurisdiction.in_(regions)).all()
        else:
            regs = q.all()

    elif risk_tier == "limited":
        # Transparency requirements in matching regions
        if regions:
            regs = q.filter(Regulation.jurisdiction.in_(regions)).filter(
                Regulation.short_name.ilike("%Art. 50%") |
                Regulation.short_name.ilike("%Art. 52%") |
                Regulation.short_name.ilike("%transparency%") |
                Regulation.category.ilike("%transparency%")
            ).all()
            # If nothing specific, broaden to all in regions
            if not regs:
                regs = q.filter(Regulation.jurisdiction.in_(regions)).all()
        else:
            regs = []

    else:  # minimal or unknown
        regs = []

    return [
        {
            "id": reg.id,
            "name": reg.name,
            "short_name": reg.short_name,
            "jurisdiction": reg.jurisdiction,
            "category": reg.category,
            "url": reg.url,
        }
        for reg in regs
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_ai_system(system: AISystem, db: Session) -> Dict[str, Any]:
    """
    Classify an AI system's risk tier per EU AI Act Annex III.

    Args:
        system: AISystem ORM object.
        db:     SQLAlchemy Session (used to fetch applicable regulations).

    Returns:
        {
            "risk_tier":              str,   # unacceptable | high | limited | minimal
            "reasoning":              str,
            "classification_method":  str,   # rule_based | llm | rule_based+llm
            "applicable_regulations": list,  # [{id, name, short_name, jurisdiction, …}]
        }
    """
    search_text = _build_search_text(system)

    rule_tier, rule_reason = _rule_based_classify(search_text)

    if rule_tier is not None:
        # Strong rule-based match
        tier = rule_tier
        reasoning = rule_reason
        method = "rule_based"
    else:
        # Uncertain – call LLM
        tier, reasoning = _llm_classify(system)
        method = "llm"

    applicable_regs = _get_applicable_regulations(
        db=db,
        risk_tier=tier,
        deployment_regions=system.deployment_regions or [],
    )

    return {
        "risk_tier": tier,
        "reasoning": reasoning,
        "classification_method": method,
        "applicable_regulations": applicable_regs,
    }

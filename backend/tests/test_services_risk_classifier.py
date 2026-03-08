"""
Tests for the risk_classifier service.
Tests rule-based classification without LLM calls.
For unclassified systems (no rule match), LLM is mocked to return 'minimal'.
"""

import uuid
import pytest
from unittest.mock import patch, MagicMock

from app.services.risk_classifier import (
    _build_search_text,
    _rule_based_classify,
    classify_ai_system,
)
from app.store.models import AISystem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_system(
    name="Test System",
    purpose="",
    description="",
    data_types=None,
    deployment_regions=None,
    org_id="test-org",
):
    """Build an AISystem-like object for testing (no DB required)."""
    system = AISystem(
        id=str(uuid.uuid4()),
        name=name,
        purpose=purpose,
        description=description,
        data_types=data_types or [],
        deployment_regions=deployment_regions or ["EU"],
        risk_classification="unclassified",
        org_id=org_id,
    )
    return system


# ---------------------------------------------------------------------------
# _build_search_text
# ---------------------------------------------------------------------------

class TestBuildSearchText:
    def test_combines_all_fields(self):
        system = _make_system(
            name="My System",
            purpose="hiring",
            description="screens resumes",
            data_types=["PII", "employment"],
        )
        text = _build_search_text(system)
        assert "hiring" in text
        assert "screens resumes" in text
        assert "my system" in text
        assert "pii" in text

    def test_handles_none_fields_gracefully(self):
        system = _make_system()
        text = _build_search_text(system)
        assert isinstance(text, str)

    def test_returns_lowercase(self):
        system = _make_system(purpose="BIOMETRIC IDENTIFICATION")
        text = _build_search_text(system)
        assert text == text.lower()


# ---------------------------------------------------------------------------
# _rule_based_classify — UNACCEPTABLE tier
# ---------------------------------------------------------------------------

class TestUnacceptableClassification:
    def test_social_scoring_classified_unacceptable(self):
        system = _make_system(purpose="social scoring system for citizen behaviour")
        tier, reason = _rule_based_classify(_build_search_text(system))
        assert tier == "unacceptable"
        assert reason is not None

    def test_social_credit_classified_unacceptable(self):
        system = _make_system(description="social credit scoring based on citizen activity")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "unacceptable"

    def test_subliminal_manipulation_classified_unacceptable(self):
        system = _make_system(purpose="subliminal manipulation of user behaviour")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "unacceptable"

    def test_biometric_categorisation_classified_unacceptable(self):
        system = _make_system(purpose="biometric categorisation by race and religion")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "unacceptable"

    def test_mass_facial_scraping_classified_unacceptable(self):
        system = _make_system(purpose="scrape facial image databases at scale")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "unacceptable"


# ---------------------------------------------------------------------------
# _rule_based_classify — HIGH RISK tier
# ---------------------------------------------------------------------------

class TestHighRiskClassification:
    def test_biometric_identification_classified_high(self):
        system = _make_system(purpose="biometric identification using facial recognition")
        tier, reason = _rule_based_classify(_build_search_text(system))
        assert tier == "high"
        assert "biometric" in reason.lower() or "Annex III" in reason

    def test_facial_recognition_classified_high(self):
        system = _make_system(purpose="facial recognit for building access control")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"

    def test_critical_infrastructure_classified_high(self):
        system = _make_system(purpose="manage power grid and critical infrastructure")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"

    def test_hiring_and_recruitment_classified_high(self):
        system = _make_system(purpose="hiring and recruitment screening for job applicant")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"

    def test_employment_decision_classified_high(self):
        system = _make_system(description="makes employment decision based on employee evaluation")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"

    def test_credit_scoring_classified_high(self):
        system = _make_system(purpose="credit scor for loan eligibility assessment")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"

    def test_law_enforcement_classified_high(self):
        system = _make_system(purpose="crime predict and criminal risk profiling for law enforcement")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"

    def test_education_assessment_classified_high(self):
        system = _make_system(purpose="student assessment for university admission")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"

    def test_immigration_border_classified_high(self):
        system = _make_system(purpose="immigration and border control for visa decisions")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "high"


# ---------------------------------------------------------------------------
# _rule_based_classify — LIMITED RISK tier
# ---------------------------------------------------------------------------

class TestLimitedRiskClassification:
    def test_chatbot_classified_limited(self):
        system = _make_system(purpose="chatbot for customer support queries")
        tier, reason = _rule_based_classify(_build_search_text(system))
        assert tier == "limited"
        assert reason is not None

    def test_virtual_assistant_classified_limited(self):
        system = _make_system(purpose="virtual assistant for product recommendations")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "limited"

    def test_deepfake_classified_limited(self):
        system = _make_system(purpose="generates deepfake synthetic media for entertainment")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "limited"

    def test_emotion_recognition_classified_limited(self):
        system = _make_system(purpose="emotion recognit and sentiment detection in video")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "limited"

    def test_conversational_ai_classified_limited(self):
        system = _make_system(purpose="conversational ai for banking support")
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier == "limited"


# ---------------------------------------------------------------------------
# _rule_based_classify — No match (falls through to None)
# ---------------------------------------------------------------------------

class TestMinimalRiskClassification:
    def test_general_analytics_no_rule_match(self):
        system = _make_system(
            purpose="sales analytics dashboard",
            description="Aggregates sales data for reporting",
        )
        tier, reason = _rule_based_classify(_build_search_text(system))
        # No rule matches — should return None, None (LLM fallback)
        assert tier is None
        assert reason is None

    def test_generic_software_no_rule_match(self):
        system = _make_system(
            name="Inventory Management AI",
            purpose="track inventory levels and reorder automatically",
        )
        tier, _ = _rule_based_classify(_build_search_text(system))
        assert tier is None


# ---------------------------------------------------------------------------
# classify_ai_system (full function) — with mocked LLM
# ---------------------------------------------------------------------------

class TestClassifyAISystemFull:
    def test_high_risk_system_via_rules(self, db, sample_ai_system):
        """Biometric system should be classified as high via rule_based (no LLM)."""
        sample_ai_system.purpose = "biometric identif and facial recognition"
        sample_ai_system.description = "Access control using biometric data"
        db.commit()

        result = classify_ai_system(sample_ai_system, db)
        assert result["risk_tier"] == "high"
        assert result["classification_method"] == "rule_based"
        assert "reasoning" in result
        assert "applicable_regulations" in result
        assert isinstance(result["applicable_regulations"], list)

    def test_unacceptable_system_via_rules(self, db, sample_ai_system):
        sample_ai_system.purpose = "social scoring system for citizens"
        db.commit()
        result = classify_ai_system(sample_ai_system, db)
        assert result["risk_tier"] == "unacceptable"
        assert result["classification_method"] == "rule_based"

    def test_limited_risk_chatbot_via_rules(self, db, sample_ai_system):
        sample_ai_system.purpose = "customer support chatbot"
        db.commit()
        result = classify_ai_system(sample_ai_system, db)
        assert result["risk_tier"] == "limited"
        assert result["classification_method"] == "rule_based"

    @patch("app.services.risk_classifier._llm_classify")
    def test_minimal_risk_falls_back_to_llm(self, mock_llm, db, sample_ai_system):
        """When no rule matches, LLM is called and result is returned."""
        mock_llm.return_value = ("minimal", "No specific EU AI Act risk category applies.")
        sample_ai_system.purpose = "sales data aggregation dashboard"
        sample_ai_system.description = "Aggregates sales metrics for reporting"
        db.commit()

        result = classify_ai_system(sample_ai_system, db)
        assert result["risk_tier"] == "minimal"
        assert result["classification_method"] == "llm"
        mock_llm.assert_called_once()

    @patch("app.services.risk_classifier._llm_classify")
    def test_minimal_risk_has_empty_regulations(self, mock_llm, db, sample_ai_system):
        """Minimal risk systems should have no applicable regulations."""
        mock_llm.return_value = ("minimal", "General software, no specific risk.")
        sample_ai_system.purpose = "simple data aggregation tool"
        db.commit()
        result = classify_ai_system(sample_ai_system, db)
        assert result["applicable_regulations"] == []

    def test_result_structure_is_complete(self, db, sample_ai_system):
        """The result dict must always have all required keys."""
        result = classify_ai_system(sample_ai_system, db)
        assert "risk_tier" in result
        assert "reasoning" in result
        assert "classification_method" in result
        assert "applicable_regulations" in result

    def test_regulation_mapping_eu_for_high_risk(self, db, sample_ai_system, sample_regulation):
        """High-risk systems deployed in EU should map to EU regulations."""
        sample_ai_system.purpose = "biometric identif using facial recognit"
        sample_ai_system.deployment_regions = ["EU"]
        db.commit()

        result = classify_ai_system(sample_ai_system, db)
        assert result["risk_tier"] == "high"
        # EU regulation we seeded should appear in applicable_regulations
        reg_ids = [r["id"] for r in result["applicable_regulations"]]
        assert sample_regulation.id in reg_ids

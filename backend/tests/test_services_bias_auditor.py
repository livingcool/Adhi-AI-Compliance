"""
Tests for the bias_auditor service.
Tests statistical fairness metrics: demographic parity, disparate impact ratio,
equalized odds, and edge cases.
"""

import csv
import io
import json
import pytest

from app.services.bias_auditor import (
    analyze_bias,
    _detect_protected_attributes,
    _compute_attribute_metrics,
    _is_positive,
    _safe_div,
    BiasAuditResult,
    AttributeMetrics,
)


# ---------------------------------------------------------------------------
# Helper: build CSV bytes from list of dicts
# ---------------------------------------------------------------------------

def _make_csv(rows: list, fieldnames: list = None) -> bytes:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _make_json(rows: list) -> bytes:
    return json.dumps(rows).encode("utf-8")


# ---------------------------------------------------------------------------
# BIASED DATASET — should return FAIL
# ---------------------------------------------------------------------------

class TestBiasedDataset:
    """A dataset where one gender group has a much lower positive outcome rate."""

    def _biased_csv(self) -> bytes:
        rows = []
        # Male: 90% positive hire rate
        for i in range(90):
            rows.append({"gender": "male", "outcome": "1", "age": "30"})
        for i in range(10):
            rows.append({"gender": "male", "outcome": "0", "age": "30"})
        # Female: 20% positive hire rate  (disparate impact = 0.20/0.90 ≈ 0.22 → FAIL)
        for i in range(20):
            rows.append({"gender": "female", "outcome": "1", "age": "30"})
        for i in range(80):
            rows.append({"gender": "female", "outcome": "0", "age": "30"})
        return _make_csv(rows)

    def test_biased_dataset_overall_status_fail(self):
        result = analyze_bias(self._biased_csv(), "csv")
        assert result.overall_status == "fail"

    def test_biased_dataset_disparate_impact_below_threshold(self):
        result = analyze_bias(self._biased_csv(), "csv")
        # Disparate impact ratio should be well below 0.8
        assert result.disparate_impact_ratio < 0.8

    def test_biased_dataset_demographic_parity_high(self):
        result = analyze_bias(self._biased_csv(), "csv")
        # Parity difference should be large
        assert result.demographic_parity_score > 0.1

    def test_biased_dataset_has_findings(self):
        result = analyze_bias(self._biased_csv(), "csv")
        assert len(result.summary_findings) > 0
        assert any("FAIL" in f or "bias" in f.lower() for f in result.summary_findings)

    def test_biased_dataset_has_recommendations(self):
        result = analyze_bias(self._biased_csv(), "csv")
        assert len(result.summary_recommendations) > 0

    def test_biased_dataset_protected_attr_status_fail(self):
        result = analyze_bias(self._biased_csv(), "csv")
        gender_metric = next(
            (m for m in result.per_attribute if m.attribute == "gender"), None
        )
        assert gender_metric is not None
        assert gender_metric.status == "fail"


# ---------------------------------------------------------------------------
# BALANCED DATASET — should return PASS
# ---------------------------------------------------------------------------

class TestBalancedDataset:
    def _balanced_csv(self) -> bytes:
        rows = []
        # Both genders: ~50% positive rate
        for gender in ("male", "female"):
            for _ in range(50):
                rows.append({"gender": gender, "outcome": "1"})
            for _ in range(50):
                rows.append({"gender": gender, "outcome": "0"})
        return _make_csv(rows)

    def test_balanced_dataset_overall_status_pass(self):
        result = analyze_bias(self._balanced_csv(), "csv")
        assert result.overall_status == "pass"

    def test_balanced_dataset_disparate_impact_above_threshold(self):
        result = analyze_bias(self._balanced_csv(), "csv")
        # Both groups at 50% → disparate impact = 1.0
        assert result.disparate_impact_ratio >= 0.9

    def test_balanced_dataset_demographic_parity_low(self):
        result = analyze_bias(self._balanced_csv(), "csv")
        assert result.demographic_parity_score < 0.05

    def test_balanced_dataset_gender_metric_pass(self):
        result = analyze_bias(self._balanced_csv(), "csv")
        gender_metric = next(
            (m for m in result.per_attribute if m.attribute == "gender"), None
        )
        assert gender_metric is not None
        assert gender_metric.status == "pass"


# ---------------------------------------------------------------------------
# CONDITIONAL (0.8 ≤ disparate_impact < 0.9) — should return 'conditional'
# ---------------------------------------------------------------------------

class TestConditionalDataset:
    def _conditional_csv(self) -> bytes:
        rows = []
        # Group A: 85% positive
        for _ in range(85):
            rows.append({"race": "group_a", "outcome": "1"})
        for _ in range(15):
            rows.append({"race": "group_a", "outcome": "0"})
        # Group B: 75% positive (disparate impact = 75/85 ≈ 0.882 → conditional)
        for _ in range(75):
            rows.append({"race": "group_b", "outcome": "1"})
        for _ in range(25):
            rows.append({"race": "group_b", "outcome": "0"})
        return _make_csv(rows)

    def test_conditional_overall_status(self):
        result = analyze_bias(self._conditional_csv(), "csv")
        assert result.overall_status == "conditional"

    def test_conditional_disparate_impact_in_range(self):
        result = analyze_bias(self._conditional_csv(), "csv")
        assert 0.8 <= result.disparate_impact_ratio < 0.9


# ---------------------------------------------------------------------------
# Demographic parity calculation
# ---------------------------------------------------------------------------

class TestDemographicParity:
    def test_demographic_parity_difference_correct(self):
        rows = []
        # Group A: 100% positive
        for _ in range(10):
            rows.append({"gender": "a", "outcome": "1"})
        # Group B: 0% positive
        for _ in range(10):
            rows.append({"gender": "b", "outcome": "0"})
        result = analyze_bias(_make_csv(rows), "csv")
        # Parity difference = |1.0 - 0.0| = 1.0
        assert result.demographic_parity_score == pytest.approx(1.0, abs=0.01)

    def test_equal_positive_rates_means_zero_parity_diff(self):
        rows = [
            {"gender": "a", "outcome": "1"},
            {"gender": "b", "outcome": "1"},
        ]
        result = analyze_bias(_make_csv(rows), "csv")
        assert result.demographic_parity_score == pytest.approx(0.0, abs=0.01)


# ---------------------------------------------------------------------------
# Disparate impact ratio calculation
# ---------------------------------------------------------------------------

class TestDisparateImpactRatio:
    def test_disparate_impact_ratio_formula(self):
        """Verify formula: min_rate / max_rate."""
        rows = []
        # Min group: 40%, max group: 80%
        for _ in range(4):
            rows.append({"gender": "a", "outcome": "1"})
        for _ in range(6):
            rows.append({"gender": "a", "outcome": "0"})
        for _ in range(8):
            rows.append({"gender": "b", "outcome": "1"})
        for _ in range(2):
            rows.append({"gender": "b", "outcome": "0"})

        result = analyze_bias(_make_csv(rows), "csv")
        # min=0.4, max=0.8 → 0.4/0.8 = 0.5
        assert result.disparate_impact_ratio == pytest.approx(0.5, abs=0.05)

    def test_disparate_impact_is_between_0_and_1(self):
        rows = []
        for _ in range(10):
            rows.append({"race": "x", "outcome": "1"})
        for _ in range(5):
            rows.append({"race": "y", "outcome": "1"})
        for _ in range(5):
            rows.append({"race": "y", "outcome": "0"})
        result = analyze_bias(_make_csv(rows), "csv")
        assert 0.0 <= result.disparate_impact_ratio <= 1.0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_dataset_returns_conditional(self):
        result = analyze_bias(b"gender,outcome\n", "csv")
        assert result.overall_status == "conditional"
        assert result.dataset_row_count == 0
        assert "empty" in result.summary_findings[0].lower()

    def test_single_group_no_bias(self):
        rows = [
            {"gender": "male", "outcome": "1"},
            {"gender": "male", "outcome": "0"},
        ]
        result = analyze_bias(_make_csv(rows), "csv")
        # Single group → disparate impact = 1.0 (no comparison possible)
        assert result.disparate_impact_ratio == pytest.approx(1.0, abs=0.01)

    def test_no_protected_attributes_detected(self):
        rows = [
            {"score": "100", "label": "1"},
            {"score": "80", "label": "0"},
        ]
        result = analyze_bias(_make_csv(rows), "csv")
        assert result.protected_attributes_analyzed == []
        assert result.overall_status == "conditional"
        assert len(result.summary_findings) > 0

    def test_json_format_parsed_correctly(self):
        rows = [
            {"gender": "male", "outcome": 1},
            {"gender": "female", "outcome": 1},
            {"gender": "male", "outcome": 0},
            {"gender": "female", "outcome": 0},
        ]
        result = analyze_bias(_make_json(rows), "json")
        assert result.dataset_row_count == 4
        assert result.overall_status == "pass"

    def test_dataset_row_count_correct(self):
        rows = [{"gender": "male", "outcome": "1"}] * 42
        result = analyze_bias(_make_csv(rows), "csv")
        assert result.dataset_row_count == 42

    def test_dataset_column_count_correct(self):
        rows = [{"gender": "male", "age": "30", "race": "white", "outcome": "1"}]
        result = analyze_bias(_make_csv(rows), "csv")
        assert result.dataset_column_count == 4

    def test_explicit_protected_attributes(self):
        rows = [
            {"gender": "male", "color": "blue", "outcome": "1"},
            {"gender": "female", "color": "blue", "outcome": "0"},
        ]
        # Specify 'color' as a protected attribute even though it wouldn't be auto-detected
        result = analyze_bias(_make_csv(rows), "csv", protected_attributes=["color"])
        assert "color" in result.protected_attributes_analyzed

    def test_multiple_protected_attributes(self):
        rows = []
        for gender in ("male", "female"):
            for race in ("white", "black"):
                for _ in range(10):
                    rows.append({"gender": gender, "race": race, "outcome": "1"})
                for _ in range(10):
                    rows.append({"gender": gender, "race": race, "outcome": "0"})
        result = analyze_bias(_make_csv(rows), "csv")
        assert "gender" in result.protected_attributes_analyzed
        assert "race" in result.protected_attributes_analyzed
        assert len(result.per_attribute) == 2


# ---------------------------------------------------------------------------
# _detect_protected_attributes
# ---------------------------------------------------------------------------

class TestDetectProtectedAttributes:
    def test_detects_gender(self):
        assert "gender" in _detect_protected_attributes(["gender", "salary", "outcome"])

    def test_detects_race(self):
        assert "race" in _detect_protected_attributes(["race", "id", "label"])

    def test_detects_age(self):
        assert "age" in _detect_protected_attributes(["age", "score"])

    def test_detects_ethnicity(self):
        assert "ethnicity" in _detect_protected_attributes(["ethnicity", "income"])

    def test_no_false_positives(self):
        result = _detect_protected_attributes(["score", "id", "outcome", "prediction"])
        assert result == []

    def test_case_insensitive(self):
        result = _detect_protected_attributes(["Gender", "RACE", "Age"])
        assert len(result) == 3


# ---------------------------------------------------------------------------
# _is_positive helper
# ---------------------------------------------------------------------------

class TestIsPositive:
    @pytest.mark.parametrize("value", ["1", "yes", "true", "positive", "approved", "hire", "hired", "accept", "accepted"])
    def test_positive_values(self, value):
        assert _is_positive(value) is True

    @pytest.mark.parametrize("value", ["0", "no", "false", "negative", "rejected", "denied", "2", "null"])
    def test_negative_values(self, value):
        assert _is_positive(value) is False


# ---------------------------------------------------------------------------
# _safe_div helper
# ---------------------------------------------------------------------------

class TestSafeDiv:
    def test_normal_division(self):
        assert _safe_div(1.0, 2.0) == 0.5

    def test_zero_denominator_returns_zero(self):
        assert _safe_div(5.0, 0.0) == 0.0

    def test_zero_numerator(self):
        assert _safe_div(0.0, 5.0) == 0.0

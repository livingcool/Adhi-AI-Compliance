"""
Bias Auditor service — statistical fairness analysis for AI systems.

Supported metrics:
  - Demographic parity (statistical parity difference)
  - Disparate impact ratio
  - Equalized odds (TPR + FPR difference across groups)

Thresholds for disparate impact:
  < 0.8  → FAIL
  0.8–0.9 → WARN  (stored as "conditional")
  > 0.9  → PASS
"""

from __future__ import annotations

import csv
import io
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Known protected-attribute column name patterns (case-insensitive prefix/exact)
# ---------------------------------------------------------------------------
_PROTECTED_KEYWORDS = [
    "gender", "sex", "race", "ethnicity", "age",
    "skin_tone", "skin_color", "disability", "religion", "nationality",
]


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class AttributeMetrics:
    attribute: str
    groups: List[str]
    group_positive_rates: Dict[str, float]      # P(positive | group)
    demographic_parity_difference: float        # max - min of positive rates
    disparate_impact_ratio: float               # min / max of positive rates
    equalized_odds_tpr_diff: Optional[float]    # |TPR_a - TPR_b|  (None if no labels)
    equalized_odds_fpr_diff: Optional[float]    # |FPR_a - FPR_b|
    status: str                                  # "pass" | "conditional" | "fail"
    findings: List[str]
    recommendations: List[str]


@dataclass
class BiasAuditResult:
    overall_status: str                          # "pass" | "conditional" | "fail"
    demographic_parity_score: float             # avg statistical parity diff (lower = better)
    disparate_impact_ratio: float               # worst-case ratio across attributes
    per_attribute: List[AttributeMetrics]
    dataset_row_count: int
    dataset_column_count: int
    protected_attributes_analyzed: List[str]
    summary_findings: List[str]
    summary_recommendations: List[str]
    raw_details: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_protected_attributes(columns: List[str]) -> List[str]:
    """Return columns that look like protected attributes."""
    detected = []
    for col in columns:
        lower = col.lower()
        for kw in _PROTECTED_KEYWORDS:
            if kw in lower:
                detected.append(col)
                break
    return detected


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _parse_csv(content: bytes) -> Tuple[List[str], List[Dict[str, str]]]:
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    columns = reader.fieldnames or []
    return list(columns), rows


def _parse_json(content: bytes) -> Tuple[List[str], List[Dict[str, Any]]]:
    data = json.loads(content.decode("utf-8", errors="replace"))
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and "data" in data:
        rows = data["data"]
    else:
        rows = [data]
    columns = list(rows[0].keys()) if rows else []
    return columns, rows


def _is_positive(value: Any) -> bool:
    """Heuristic: treat 1, '1', 'yes', 'true', 'positive', 'approved' as positive."""
    sv = str(value).strip().lower()
    return sv in {"1", "yes", "true", "positive", "approved", "accept", "accepted", "hire", "hired"}


def _compute_attribute_metrics(
    rows: List[Dict[str, Any]],
    attribute: str,
    outcome_col: Optional[str],
    prediction_col: Optional[str],
) -> AttributeMetrics:
    # Group rows by attribute value
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        val = str(row.get(attribute, "unknown")).strip()
        groups.setdefault(val, []).append(row)

    group_names = sorted(groups.keys())
    group_positive_rates: Dict[str, float] = {}

    for g, g_rows in groups.items():
        if prediction_col and prediction_col in g_rows[0]:
            positives = sum(1 for r in g_rows if _is_positive(r.get(prediction_col)))
        elif outcome_col and outcome_col in g_rows[0]:
            positives = sum(1 for r in g_rows if _is_positive(r.get(outcome_col)))
        else:
            positives = 0
        group_positive_rates[g] = _safe_div(positives, len(g_rows))

    rates = list(group_positive_rates.values())
    max_rate = max(rates) if rates else 0.0
    min_rate = min(rates) if rates else 0.0

    demographic_parity_diff = max_rate - min_rate
    disparate_impact = _safe_div(min_rate, max_rate) if max_rate > 0 else 1.0

    # Equalized odds (requires ground-truth outcome + model prediction)
    tpr_diff: Optional[float] = None
    fpr_diff: Optional[float] = None
    if outcome_col and prediction_col and outcome_col in rows[0] and prediction_col in rows[0]:
        tprs: Dict[str, float] = {}
        fprs: Dict[str, float] = {}
        for g, g_rows in groups.items():
            tp = fp = tn = fn = 0
            for r in g_rows:
                actual_pos = _is_positive(r.get(outcome_col))
                pred_pos = _is_positive(r.get(prediction_col))
                if actual_pos and pred_pos:
                    tp += 1
                elif actual_pos and not pred_pos:
                    fn += 1
                elif not actual_pos and pred_pos:
                    fp += 1
                else:
                    tn += 1
            tprs[g] = _safe_div(tp, tp + fn)
            fprs[g] = _safe_div(fp, fp + tn)
        tpr_vals = list(tprs.values())
        fpr_vals = list(fprs.values())
        tpr_diff = max(tpr_vals) - min(tpr_vals) if len(tpr_vals) >= 2 else 0.0
        fpr_diff = max(fpr_vals) - min(fpr_vals) if len(fpr_vals) >= 2 else 0.0

    # Determine status from disparate impact
    if disparate_impact < 0.8:
        status = "fail"
    elif disparate_impact < 0.9:
        status = "conditional"
    else:
        status = "pass"

    # Build findings
    findings: List[str] = []
    recommendations: List[str] = []

    minority = min(group_positive_rates, key=group_positive_rates.get) if group_positive_rates else None
    majority = max(group_positive_rates, key=group_positive_rates.get) if group_positive_rates else None

    if status == "fail":
        findings.append(
            f"Disparate impact ratio {disparate_impact:.3f} < 0.8 for '{attribute}': "
            f"'{minority}' has positive rate {group_positive_rates.get(minority, 0):.3f} vs "
            f"'{majority}' at {group_positive_rates.get(majority, 0):.3f}."
        )
        recommendations.append(
            f"Investigate and mitigate bias against '{minority}' group in '{attribute}'. "
            "Consider resampling, reweighting, or post-processing calibration."
        )
    elif status == "conditional":
        findings.append(
            f"Disparate impact ratio {disparate_impact:.3f} is between 0.8–0.9 for '{attribute}': "
            f"monitor closely and document justification."
        )
        recommendations.append(
            f"Apply fairness constraints or adversarial debiasing to improve '{attribute}' parity."
        )
    else:
        findings.append(
            f"Disparate impact ratio {disparate_impact:.3f} meets threshold (≥0.9) for '{attribute}'."
        )

    if tpr_diff is not None and tpr_diff > 0.1:
        findings.append(
            f"Equalized odds violation: TPR difference {tpr_diff:.3f} across '{attribute}' groups."
        )
        recommendations.append(
            f"Use equalized odds post-processing to balance true positive rates across '{attribute}' groups."
        )

    if demographic_parity_diff > 0.1:
        findings.append(
            f"Statistical parity difference {demographic_parity_diff:.3f} for '{attribute}' exceeds 0.1."
        )

    return AttributeMetrics(
        attribute=attribute,
        groups=group_names,
        group_positive_rates=group_positive_rates,
        demographic_parity_difference=demographic_parity_diff,
        disparate_impact_ratio=disparate_impact,
        equalized_odds_tpr_diff=tpr_diff,
        equalized_odds_fpr_diff=fpr_diff,
        status=status,
        findings=findings,
        recommendations=recommendations,
    )


def _find_outcome_col(columns: List[str]) -> Optional[str]:
    for name in ["outcome", "label", "target", "result", "decision", "hired", "approved"]:
        for col in columns:
            if col.lower() == name:
                return col
    return None


def _find_prediction_col(columns: List[str]) -> Optional[str]:
    for name in ["prediction", "predicted", "score", "pred", "model_output"]:
        for col in columns:
            if col.lower() == name:
                return col
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_bias(
    file_content: bytes,
    file_type: str,                             # "csv" or "json"
    protected_attributes: Optional[List[str]] = None,
) -> BiasAuditResult:
    """
    Perform statistical bias analysis on a dataset.

    Args:
        file_content: Raw bytes of the uploaded file.
        file_type: "csv" or "json".
        protected_attributes: Optional explicit list. Auto-detected if None.

    Returns:
        BiasAuditResult with per-attribute metrics and overall status.
    """
    if file_type == "json":
        columns, rows = _parse_json(file_content)
    else:
        columns, rows = _parse_csv(file_content)

    if not rows:
        return BiasAuditResult(
            overall_status="conditional",
            demographic_parity_score=0.0,
            disparate_impact_ratio=1.0,
            per_attribute=[],
            dataset_row_count=0,
            dataset_column_count=len(columns),
            protected_attributes_analyzed=[],
            summary_findings=["Dataset is empty — no analysis performed."],
            summary_recommendations=["Upload a non-empty dataset for bias analysis."],
        )

    # Determine which attributes to analyze
    if protected_attributes:
        attrs_to_analyze = [a for a in protected_attributes if a in columns]
    else:
        attrs_to_analyze = _detect_protected_attributes(columns)

    outcome_col = _find_outcome_col(columns)
    prediction_col = _find_prediction_col(columns)

    per_attribute: List[AttributeMetrics] = []
    for attr in attrs_to_analyze:
        metrics = _compute_attribute_metrics(rows, attr, outcome_col, prediction_col)
        per_attribute.append(metrics)

    # Aggregate overall status (worst-case)
    statuses = [m.status for m in per_attribute]
    if "fail" in statuses:
        overall_status = "fail"
    elif "conditional" in statuses:
        overall_status = "conditional"
    else:
        overall_status = "pass"

    # Aggregate scores
    if per_attribute:
        avg_parity_diff = sum(m.demographic_parity_difference for m in per_attribute) / len(per_attribute)
        worst_di = min(m.disparate_impact_ratio for m in per_attribute)
    else:
        avg_parity_diff = 0.0
        worst_di = 1.0
        overall_status = "conditional"

    # Build summary
    summary_findings: List[str] = []
    summary_recommendations: List[str] = []

    if not attrs_to_analyze:
        summary_findings.append(
            "No protected attributes detected or specified. "
            "Add columns named gender, race, age, skin_tone, etc. for bias analysis."
        )
        summary_recommendations.append(
            "Include protected attribute columns and rerun the audit."
        )
    else:
        fail_attrs = [m.attribute for m in per_attribute if m.status == "fail"]
        warn_attrs = [m.attribute for m in per_attribute if m.status == "conditional"]
        if fail_attrs:
            summary_findings.append(f"FAIL: Significant bias detected in attributes: {', '.join(fail_attrs)}.")
        if warn_attrs:
            summary_findings.append(f"WARN: Marginal bias detected in attributes: {', '.join(warn_attrs)}.")
        if not fail_attrs and not warn_attrs:
            summary_findings.append("All analyzed attributes meet fairness thresholds.")

        for m in per_attribute:
            summary_recommendations.extend(m.recommendations)

    return BiasAuditResult(
        overall_status=overall_status,
        demographic_parity_score=round(avg_parity_diff, 4),
        disparate_impact_ratio=round(worst_di, 4),
        per_attribute=per_attribute,
        dataset_row_count=len(rows),
        dataset_column_count=len(columns),
        protected_attributes_analyzed=attrs_to_analyze,
        summary_findings=summary_findings,
        summary_recommendations=summary_recommendations,
        raw_details={
            "outcome_column": outcome_col,
            "prediction_column": prediction_col,
            "columns": columns,
        },
    )

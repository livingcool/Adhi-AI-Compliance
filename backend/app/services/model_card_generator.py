"""
Model Card Generator — produces EU AI Act Article 13–aligned model cards.

Functions:
  generate_model_card(ai_system, bias_audits, compliance_checks) -> dict
  export_model_card_pdf(model_card) -> bytes
"""

from __future__ import annotations

import html
from datetime import datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# HTML/CSS template for PDF export
# ---------------------------------------------------------------------------

_PDF_CSS = """
body { font-family: Arial, sans-serif; font-size: 13px; color: #1a1a1a; margin: 40px; }
h1 { font-size: 22px; color: #1e3a5f; border-bottom: 3px solid #1e3a5f; padding-bottom: 8px; }
h2 { font-size: 16px; color: #2c5f8a; border-bottom: 1px solid #c0d8ef; padding-bottom: 4px; margin-top: 28px; }
h3 { font-size: 14px; color: #444; margin-bottom: 4px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th { background: #1e3a5f; color: #fff; padding: 7px 10px; text-align: left; font-size: 12px; }
td { border: 1px solid #dde; padding: 6px 10px; vertical-align: top; font-size: 12px; }
tr:nth-child(even) td { background: #f4f8fc; }
.badge-pass { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.badge-fail { background: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.badge-warn { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.badge-na   { background: #e2e3e5; color: #383d41; padding: 2px 8px; border-radius: 4px; }
ul { padding-left: 20px; }
li { margin: 3px 0; }
.meta { color: #666; font-size: 11px; margin-bottom: 20px; }
.section-box { border: 1px solid #dde; border-radius: 6px; padding: 14px; margin: 10px 0; }
"""


def _badge(status: str) -> str:
    s = (status or "").lower()
    if s in ("pass", "compliant", "low"):
        return f'<span class="badge-pass">{html.escape(status)}</span>'
    elif s in ("fail", "non_compliant", "critical", "high"):
        return f'<span class="badge-fail">{html.escape(status)}</span>'
    elif s in ("conditional", "partial", "medium", "warn"):
        return f'<span class="badge-warn">{html.escape(status)}</span>'
    else:
        return f'<span class="badge-na">{html.escape(status)}</span>'


def _esc(v: Any) -> str:
    return html.escape(str(v)) if v is not None else "—"


# ---------------------------------------------------------------------------
# Core generator
# ---------------------------------------------------------------------------

def generate_model_card(
    ai_system: Any,
    bias_audits: List[Any],
    compliance_checks: List[Any],
) -> Dict[str, Any]:
    """
    Generate a structured model card following EU AI Act Article 13.

    Args:
        ai_system: SQLAlchemy AISystem ORM instance.
        bias_audits: List of BiasAudit ORM instances for this system.
        compliance_checks: List of ComplianceCheck ORM instances for this system.

    Returns:
        dict — the full model card, suitable for JSON storage.
    """
    now = datetime.utcnow().isoformat()

    # --- Section 1: Model Details ---
    model_details: Dict[str, Any] = {
        "name": ai_system.name,
        "system_id": ai_system.id,
        "version": "1.0",
        "provider": ai_system.model_provider or "Unknown",
        "type": ai_system.purpose or "General AI System",
        "description": ai_system.description or "",
        "risk_classification": ai_system.risk_classification or "unclassified",
        "is_high_risk": ai_system.is_high_risk,
        "deployment_regions": ai_system.deployment_regions or [],
        "data_types": ai_system.data_types or [],
        "organization_id": ai_system.org_id,
        "card_generated_at": now,
    }

    # --- Section 2: Intended Use ---
    intended_use: Dict[str, Any] = {
        "primary_use": ai_system.purpose or "Not specified",
        "intended_users": "See system documentation",
        "deployment_contexts": ai_system.deployment_regions or [],
        "out_of_scope_uses": [
            "Use in unacceptable-risk domains without explicit regulatory clearance",
            "Automated decisions on individuals without human oversight in high-risk domains",
            "Processing special-category personal data beyond declared scope",
        ],
    }

    # --- Section 3: Training Data Summary ---
    data_summary: Dict[str, Any] = {
        "data_types_used": ai_system.data_types or [],
        "data_sources": "Not disclosed — see technical documentation",
        "preprocessing": "Not disclosed",
        "known_limitations": (
            "Training data composition, collection periods, and geographic coverage "
            "have not been fully disclosed. Users should validate performance on "
            "their specific deployment context."
        ),
    }

    # --- Section 4: Performance Metrics ---
    performance: Dict[str, Any] = {
        "compliance_score": ai_system.compliance_score,
        "evaluation_notes": (
            "Compliance score reflects aggregated regulatory gap analysis. "
            "Task-specific accuracy metrics should be documented in the technical dossier."
        ),
    }

    # --- Section 5: Bias Evaluation ---
    bias_evaluations: List[Dict[str, Any]] = []
    latest_bias_status = "not_evaluated"
    if bias_audits:
        latest = bias_audits[0]
        latest_bias_status = latest.overall_status or "not_evaluated"
        for audit in bias_audits:
            findings = audit.findings or {}
            bias_evaluations.append({
                "audit_id": audit.id,
                "audit_date": audit.audit_date.isoformat() if audit.audit_date else None,
                "overall_status": audit.overall_status,
                "demographic_parity_score": audit.demographic_parity_score,
                "disparate_impact_ratio": audit.disparate_impact_ratio,
                "dataset_description": audit.dataset_description,
                "summary_findings": findings.get("summary_findings", []),
                "summary_recommendations": findings.get("summary_recommendations", []),
                "per_attribute": findings.get("per_attribute", []),
            })

    bias_section: Dict[str, Any] = {
        "latest_status": latest_bias_status,
        "evaluations": bias_evaluations,
        "methodology": (
            "Statistical fairness analysis using demographic parity, disparate impact ratio "
            "(80% rule), equalized odds (TPR/FPR parity), and statistical parity difference. "
            "Threshold: disparate_impact < 0.8 = FAIL, 0.8–0.9 = CONDITIONAL, ≥0.9 = PASS."
        ),
        "protected_attributes_evaluated": (
            list({
                attr
                for audit in bias_audits
                for attr in (audit.findings or {}).get("protected_attributes_analyzed", [])
            })
            if bias_audits else []
        ),
    }

    # --- Section 6: Limitations & Risks ---
    risk_factors: List[str] = []
    if ai_system.is_high_risk:
        risk_factors.append("Classified as HIGH-RISK under EU AI Act — mandatory conformity assessment required.")
    if ai_system.risk_classification == "unacceptable":
        risk_factors.append("Risk classification is UNACCEPTABLE — deployment prohibited under EU AI Act.")
    if latest_bias_status == "fail":
        risk_factors.append("Latest bias audit FAILED — discriminatory outcomes detected; remediation required.")
    elif latest_bias_status in ("conditional", "not_evaluated"):
        risk_factors.append("Bias evaluation is incomplete or marginal — enhanced monitoring recommended.")
    risk_factors.append(
        "AI system outputs may not be reliable outside the intended deployment context."
    )
    risk_factors.append(
        "Human oversight must be maintained for all consequential decisions."
    )

    limitations: Dict[str, Any] = {
        "known_risks": risk_factors,
        "human_oversight_required": ai_system.is_high_risk or True,
        "out_of_distribution_warning": (
            "Performance may degrade significantly on data distributions not represented "
            "in the training or evaluation datasets."
        ),
    }

    # --- Section 7: Compliance Status ---
    compliance_summary: List[Dict[str, Any]] = []
    for check in compliance_checks:
        compliance_summary.append({
            "regulation_id": check.regulation_id,
            "status": check.status,
            "priority": check.priority,
            "gap_description": check.gap_description,
            "remediation_steps": check.remediation_steps,
            "deadline": check.deadline.isoformat() if check.deadline else None,
            "checked_at": check.checked_at.isoformat() if check.checked_at else None,
        })

    compliance_section: Dict[str, Any] = {
        "checks": compliance_summary,
        "total": len(compliance_summary),
        "compliant_count": sum(1 for c in compliance_checks if c.status == "compliant"),
        "non_compliant_count": sum(1 for c in compliance_checks if c.status == "non_compliant"),
        "partial_count": sum(1 for c in compliance_checks if c.status == "partial"),
        "pending_count": sum(1 for c in compliance_checks if c.status == "pending"),
        "critical_gaps": [
            c.gap_description
            for c in compliance_checks
            if c.priority == "critical" and c.status != "compliant"
        ],
    }

    # --- Assemble full card ---
    return {
        "schema_version": "1.0",
        "eu_ai_act_article": "Article 13 — Transparency and provision of information",
        "generated_at": now,
        "model_details": model_details,
        "intended_use": intended_use,
        "training_data": data_summary,
        "performance": performance,
        "bias_evaluation": bias_section,
        "limitations_and_risks": limitations,
        "compliance_status": compliance_section,
    }


# ---------------------------------------------------------------------------
# PDF export
# ---------------------------------------------------------------------------

def export_model_card_pdf(model_card: Dict[str, Any]) -> bytes:
    """
    Render the model card as PDF bytes.

    Uses weasyprint if available; falls back to returning the HTML as bytes.
    """
    html_content = _render_html(model_card)
    try:
        from weasyprint import HTML as WeasyHTML  # type: ignore
        return WeasyHTML(string=html_content).write_pdf()
    except ImportError:
        # weasyprint not installed — return HTML bytes with a PDF-like content type hint
        return html_content.encode("utf-8")


def _render_html(card: Dict[str, Any]) -> str:
    md = card.get("model_details", {})
    iu = card.get("intended_use", {})
    td = card.get("training_data", {})
    perf = card.get("performance", {})
    bias = card.get("bias_evaluation", {})
    limits = card.get("limitations_and_risks", {})
    comp = card.get("compliance_status", {})

    rows_compliance = ""
    for c in comp.get("checks", []):
        rows_compliance += (
            f"<tr><td>{_esc(c.get('regulation_id'))}</td>"
            f"<td>{_badge(c.get('status',''))}</td>"
            f"<td>{_badge(c.get('priority',''))}</td>"
            f"<td>{_esc(c.get('gap_description'))}</td>"
            f"<td>{_esc(c.get('deadline'))}</td></tr>"
        )

    rows_bias = ""
    for b in bias.get("evaluations", []):
        rows_bias += (
            f"<tr><td>{_esc(b.get('audit_date'))}</td>"
            f"<td>{_badge(b.get('overall_status',''))}</td>"
            f"<td>{_esc(b.get('demographic_parity_score'))}</td>"
            f"<td>{_esc(b.get('disparate_impact_ratio'))}</td>"
            f"<td>{_esc(b.get('dataset_description'))}</td></tr>"
        )

    risk_items = "".join(f"<li>{_esc(r)}</li>" for r in limits.get("known_risks", []))
    oos_items = "".join(f"<li>{_esc(u)}</li>" for u in iu.get("out_of_scope_uses", []))
    data_types = ", ".join(_esc(d) for d in md.get("data_types", [])) or "—"
    regions = ", ".join(_esc(r) for r in md.get("deployment_regions", [])) or "—"
    protected_attrs = ", ".join(_esc(a) for a in bias.get("protected_attributes_evaluated", [])) or "—"
    critical_gaps = "".join(
        f"<li>{_esc(g)}</li>" for g in comp.get("critical_gaps", [])
    ) or "<li>None identified</li>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Model Card — {_esc(md.get('name', 'AI System'))}</title>
  <style>{_PDF_CSS}</style>
</head>
<body>
  <h1>Model Card — {_esc(md.get('name', 'AI System'))}</h1>
  <p class="meta">
    Generated: {_esc(card.get('generated_at', ''))} &nbsp;|&nbsp;
    Schema: {_esc(card.get('schema_version', '1.0'))} &nbsp;|&nbsp;
    {_esc(card.get('eu_ai_act_article', ''))}
  </p>

  <h2>1. Model Details</h2>
  <div class="section-box">
    <table>
      <tr><th>Field</th><th>Value</th></tr>
      <tr><td>Name</td><td>{_esc(md.get('name'))}</td></tr>
      <tr><td>System ID</td><td>{_esc(md.get('system_id'))}</td></tr>
      <tr><td>Provider</td><td>{_esc(md.get('provider'))}</td></tr>
      <tr><td>Type / Purpose</td><td>{_esc(md.get('type'))}</td></tr>
      <tr><td>Risk Classification</td><td>{_badge(md.get('risk_classification',''))}</td></tr>
      <tr><td>High-Risk Flag</td><td>{'Yes' if md.get('is_high_risk') else 'No'}</td></tr>
      <tr><td>Deployment Regions</td><td>{regions}</td></tr>
      <tr><td>Data Types</td><td>{data_types}</td></tr>
    </table>
    <p>{_esc(md.get('description'))}</p>
  </div>

  <h2>2. Intended Use</h2>
  <div class="section-box">
    <p><strong>Primary Use:</strong> {_esc(iu.get('primary_use'))}</p>
    <p><strong>Intended Users:</strong> {_esc(iu.get('intended_users'))}</p>
    <p><strong>Out-of-Scope Uses:</strong></p>
    <ul>{oos_items}</ul>
  </div>

  <h2>3. Training Data</h2>
  <div class="section-box">
    <p><strong>Data Types:</strong> {data_types}</p>
    <p><strong>Sources:</strong> {_esc(td.get('data_sources'))}</p>
    <p><strong>Known Limitations:</strong> {_esc(td.get('known_limitations'))}</p>
  </div>

  <h2>4. Performance Metrics</h2>
  <div class="section-box">
    <p><strong>Compliance Score:</strong> {_esc(perf.get('compliance_score'))}</p>
    <p>{_esc(perf.get('evaluation_notes'))}</p>
  </div>

  <h2>5. Bias Evaluation</h2>
  <div class="section-box">
    <p><strong>Latest Status:</strong> {_badge(bias.get('latest_status',''))}</p>
    <p><strong>Protected Attributes Evaluated:</strong> {protected_attrs}</p>
    <p><strong>Methodology:</strong> {_esc(bias.get('methodology'))}</p>
    {'<table><tr><th>Date</th><th>Status</th><th>Parity Diff</th><th>DI Ratio</th><th>Dataset</th></tr>' + rows_bias + '</table>' if rows_bias else '<p>No bias audits available.</p>'}
  </div>

  <h2>6. Limitations &amp; Risks</h2>
  <div class="section-box">
    <ul>{risk_items}</ul>
    <p><strong>Out-of-distribution warning:</strong> {_esc(limits.get('out_of_distribution_warning'))}</p>
  </div>

  <h2>7. Compliance Status</h2>
  <div class="section-box">
    <p>
      Total: {comp.get('total', 0)} &nbsp;|&nbsp;
      Compliant: {comp.get('compliant_count', 0)} &nbsp;|&nbsp;
      Non-Compliant: {comp.get('non_compliant_count', 0)} &nbsp;|&nbsp;
      Partial: {comp.get('partial_count', 0)} &nbsp;|&nbsp;
      Pending: {comp.get('pending_count', 0)}
    </p>
    <p><strong>Critical Gaps:</strong></p>
    <ul>{critical_gaps}</ul>
    {'<table><tr><th>Regulation</th><th>Status</th><th>Priority</th><th>Gap</th><th>Deadline</th></tr>' + rows_compliance + '</table>' if rows_compliance else '<p>No compliance checks recorded.</p>'}
  </div>
</body>
</html>"""

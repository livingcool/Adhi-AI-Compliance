"""
Report Generator Service.

Generates compliance reports in HTML, CSV, and PDF formats for an organisation.
"""

import csv
import io
import textwrap
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.store.models import AISystem, BiasAudit, ComplianceCheck, Incident, Regulation


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_STATUS_SCORE: Dict[str, int] = {
    "compliant": 100,
    "partial": 50,
    "pending": 25,
    "non_compliant": 0,
}

_STATUS_BADGE: Dict[str, str] = {
    "compliant":     '<span style="background:#27ae60;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">Compliant</span>',
    "partial":       '<span style="background:#f39c12;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">Partial</span>',
    "pending":       '<span style="background:#95a5a6;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">Pending</span>',
    "non_compliant": '<span style="background:#e74c3c;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">Non-Compliant</span>',
}

_PRIORITY_BADGE: Dict[str, str] = {
    "critical": '<span style="background:#c0392b;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">Critical</span>',
    "high":     '<span style="background:#e74c3c;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">High</span>',
    "medium":   '<span style="background:#f39c12;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">Medium</span>',
    "low":      '<span style="background:#27ae60;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em">Low</span>',
}

_BASE_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
       margin: 0; padding: 0; color: #2c3e50; background: #f8f9fa; }
.page { max-width: 1000px; margin: 0 auto; padding: 40px 24px; }
h1 { color: #1a252f; font-size: 2em; margin-bottom: 4px; }
h2 { color: #2c3e50; font-size: 1.4em; border-bottom: 2px solid #3498db;
     padding-bottom: 6px; margin-top: 32px; }
h3 { color: #34495e; font-size: 1.1em; }
.cover { background: linear-gradient(135deg, #1a252f 0%, #2c3e50 100%);
         color: #fff; padding: 60px 40px; border-radius: 8px; margin-bottom: 40px; }
.cover h1 { color: #fff; font-size: 2.4em; margin-bottom: 8px; }
.cover .subtitle { color: #bdc3c7; font-size: 1em; }
.score-pill { display: inline-block; background: #3498db; color: #fff;
              font-size: 2em; font-weight: bold; padding: 8px 24px;
              border-radius: 50px; margin-top: 12px; }
table { width: 100%; border-collapse: collapse; margin: 12px 0 24px; font-size: 0.9em; }
th { background: #2c3e50; color: #fff; padding: 10px 12px; text-align: left; }
td { padding: 9px 12px; border-bottom: 1px solid #e0e0e0; vertical-align: top; }
tr:nth-child(even) td { background: #f4f6f8; }
.gap-text { font-size: 0.85em; color: #555; max-width: 300px; }
.rec-item { margin: 8px 0; padding: 10px 14px; background: #fff;
            border-left: 4px solid #3498db; border-radius: 4px; font-size: 0.9em; }
.rec-item.critical { border-color: #c0392b; }
.rec-item.high     { border-color: #e74c3c; }
.rec-item.medium   { border-color: #f39c12; }
.rec-item.low      { border-color: #27ae60; }
.stat-grid { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0 28px; }
.stat-card { background: #fff; border-radius: 8px; padding: 16px 20px;
             box-shadow: 0 2px 6px rgba(0,0,0,.08); flex: 1; min-width: 140px; }
.stat-card .val { font-size: 1.9em; font-weight: bold; color: #2c3e50; }
.stat-card .lbl { font-size: 0.8em; color: #7f8c8d; text-transform: uppercase;
                  letter-spacing: 0.05em; margin-top: 4px; }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #ddd;
         font-size: 0.8em; color: #95a5a6; text-align: center; }
"""


def _fetch_org_data(org_id: str, db: Session) -> Dict[str, Any]:
    """Fetch all data for an organisation needed across report functions."""
    systems = db.query(AISystem).filter(AISystem.org_id == org_id).all()
    system_ids = [s.id for s in systems]

    checks: List[ComplianceCheck] = []
    incidents: List[Incident] = []
    audits: List[BiasAudit] = []

    if system_ids:
        checks = (
            db.query(ComplianceCheck)
            .filter(ComplianceCheck.org_id == org_id)
            .order_by(ComplianceCheck.checked_at.desc())
            .all()
        )
        incidents = (
            db.query(Incident)
            .filter(Incident.org_id == org_id)
            .order_by(Incident.detected_at.desc())
            .all()
        )
        audits = (
            db.query(BiasAudit)
            .filter(BiasAudit.org_id == org_id)
            .order_by(BiasAudit.audit_date.desc())
            .all()
        )

    # Build regulation lookup
    reg_ids = list({c.regulation_id for c in checks})
    regs: List[Regulation] = []
    if reg_ids:
        regs = db.query(Regulation).filter(Regulation.id.in_(reg_ids)).all()
    reg_map: Dict[str, Regulation] = {r.id: r for r in regs}

    return {
        "systems": systems,
        "checks": checks,
        "incidents": incidents,
        "audits": audits,
        "reg_map": reg_map,
    }


def _compute_overall_score(checks: List[ComplianceCheck]) -> float:
    """Average compliance score across all checks (0–100)."""
    if not checks:
        return 0.0
    scores = [_STATUS_SCORE.get(c.status, 0) for c in checks]
    return round(sum(scores) / len(scores), 1)


def _risk_distribution(systems: List[AISystem]) -> Dict[str, int]:
    dist: Dict[str, int] = {"unacceptable": 0, "high": 0, "limited": 0, "minimal": 0, "unclassified": 0}
    for s in systems:
        key = s.risk_classification or "unclassified"
        dist[key] = dist.get(key, 0) + 1
    return dist


def _system_compliance_rows(
    systems: List[AISystem],
    checks: List[ComplianceCheck],
) -> List[Dict[str, Any]]:
    """Aggregate compliance score per system."""
    from collections import defaultdict
    by_system: Dict[str, List[ComplianceCheck]] = defaultdict(list)
    for c in checks:
        by_system[c.ai_system_id].append(c)

    rows = []
    for s in systems:
        sys_checks = by_system[s.id]
        score = _compute_overall_score(sys_checks) if sys_checks else None
        non_compliant = sum(1 for c in sys_checks if c.status == "non_compliant")
        partial = sum(1 for c in sys_checks if c.status == "partial")
        critical_gaps = sum(1 for c in sys_checks if c.priority == "critical")
        rows.append({
            "system": s,
            "checks": sys_checks,
            "score": score,
            "non_compliant": non_compliant,
            "partial": partial,
            "critical_gaps": critical_gaps,
        })
    return rows


def _stat_card(value: Any, label: str) -> str:
    return (
        f'<div class="stat-card">'
        f'<div class="val">{value}</div>'
        f'<div class="lbl">{label}</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# generate_compliance_report
# ---------------------------------------------------------------------------

def generate_compliance_report(org_id: str, db: Session, org_name: Optional[str] = None) -> str:
    """
    Generate a full HTML compliance audit report.

    Returns:
        HTML string with cover page, system breakdown, gap analysis,
        risk distribution, recommendations, and incidents summary.
    """
    data = _fetch_org_data(org_id, db)
    systems = data["systems"]
    checks = data["checks"]
    incidents = data["incidents"]
    reg_map = data["reg_map"]

    org_label = org_name or org_id
    report_date = datetime.utcnow().strftime("%B %d, %Y")
    overall_score = _compute_overall_score(checks)
    risk_dist = _risk_distribution(systems)
    sys_rows = _system_compliance_rows(systems, checks)

    non_compliant_count = sum(1 for c in checks if c.status == "non_compliant")
    partial_count = sum(1 for c in checks if c.status == "partial")
    compliant_count = sum(1 for c in checks if c.status == "compliant")

    # --- Cover / Stats section ---
    cover = f"""
<div class="cover">
  <h1>AI Compliance Audit Report</h1>
  <div class="subtitle">{org_label} &nbsp;|&nbsp; {report_date}</div>
  <div class="score-pill">{overall_score:.1f} / 100</div>
  <div class="subtitle" style="margin-top:8px">Overall Compliance Score</div>
</div>

<div class="stat-grid">
  {_stat_card(len(systems), "AI Systems")}
  {_stat_card(len(checks), "Checks Run")}
  {_stat_card(compliant_count, "Compliant")}
  {_stat_card(partial_count, "Partial")}
  {_stat_card(non_compliant_count, "Non-Compliant")}
  {_stat_card(len(incidents), "Incidents")}
</div>
"""

    # --- Per-system breakdown table ---
    sys_table_rows = ""
    for row in sys_rows:
        s = row["system"]
        score_display = f"{row['score']:.1f}" if row["score"] is not None else "N/A"
        risk_cls = s.risk_classification or "unclassified"
        sys_table_rows += f"""
<tr>
  <td><strong>{s.name}</strong><br><span class="gap-text">{s.purpose or ''}</span></td>
  <td>{risk_cls.title()}</td>
  <td>{score_display}</td>
  <td>{row['non_compliant']}</td>
  <td>{row['partial']}</td>
  <td>{row['critical_gaps']}</td>
</tr>"""

    system_table = f"""
<h2>System Compliance Breakdown</h2>
<table>
  <thead>
    <tr>
      <th>AI System</th><th>Risk Tier</th><th>Score</th>
      <th>Non-Compliant</th><th>Partial</th><th>Critical Gaps</th>
    </tr>
  </thead>
  <tbody>{sys_table_rows}</tbody>
</table>
""" if sys_table_rows else "<h2>System Compliance Breakdown</h2><p>No AI systems found for this organisation.</p>"

    # --- Gap analysis summary ---
    gap_rows = ""
    for c in sorted(checks, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.priority, 4)):
        if c.status in ("non_compliant", "partial") and c.gap_description:
            reg = reg_map.get(c.regulation_id)
            reg_label = reg.short_name if reg else c.regulation_id
            status_badge = _STATUS_BADGE.get(c.status, c.status)
            priority_badge = _PRIORITY_BADGE.get(c.priority, c.priority)
            gap_rows += f"""
<tr>
  <td>{reg_label}</td>
  <td>{status_badge}</td>
  <td>{priority_badge}</td>
  <td class="gap-text">{c.gap_description or '—'}</td>
</tr>"""

    gap_section = f"""
<h2>Gap Analysis Summary</h2>
<table>
  <thead><tr><th>Regulation</th><th>Status</th><th>Priority</th><th>Gap Description</th></tr></thead>
  <tbody>{gap_rows if gap_rows else '<tr><td colspan="4">No compliance gaps identified.</td></tr>'}</tbody>
</table>
"""

    # --- Risk distribution ---
    risk_rows = "".join(
        f'<tr><td>{tier.title()}</td><td>{count}</td><td>{"█" * count}</td></tr>'
        for tier, count in risk_dist.items()
        if count > 0
    )
    risk_section = f"""
<h2>Risk Distribution</h2>
<table>
  <thead><tr><th>Risk Tier</th><th>Count</th><th>Visual</th></tr></thead>
  <tbody>{risk_rows if risk_rows else '<tr><td colspan="3">No systems classified yet.</td></tr>'}</tbody>
</table>
"""

    # --- Recommendations ---
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    rec_checks = [c for c in checks if c.remediation_steps and c.status != "compliant"]
    rec_checks.sort(key=lambda x: priority_order.get(x.priority, 4))

    rec_items = ""
    for c in rec_checks[:20]:  # cap at 20 recommendations
        reg = reg_map.get(c.regulation_id)
        reg_label = reg.short_name if reg else "Unknown Regulation"
        steps = c.remediation_steps or ""
        rec_items += f"""
<div class="rec-item {c.priority}">
  <strong>[{c.priority.upper()}] {reg_label}</strong><br>
  <span class="gap-text">{steps[:300]}{'…' if len(steps) > 300 else ''}</span>
</div>"""

    rec_section = f"""
<h2>Recommendations (Prioritised)</h2>
{rec_items if rec_items else '<p>No remediation actions required at this time.</p>'}
"""

    # --- Incidents summary ---
    inc_rows = ""
    for inc in incidents[:10]:
        inc_rows += f"""
<tr>
  <td>{inc.incident_type or 'N/A'}</td>
  <td>{inc.severity}</td>
  <td>{inc.status}</td>
  <td>{inc.detected_at.strftime('%Y-%m-%d')}</td>
  <td class="gap-text">{(inc.description or '')[:120]}</td>
</tr>"""

    inc_section = f"""
<h2>Incidents Summary</h2>
<table>
  <thead><tr><th>Type</th><th>Severity</th><th>Status</th><th>Detected</th><th>Description</th></tr></thead>
  <tbody>{inc_rows if inc_rows else '<tr><td colspan="5">No incidents recorded.</td></tr>'}</tbody>
</table>
"""

    footer = f"""
<footer>
  Generated by Adhi Compliance Platform &nbsp;|&nbsp; {report_date} &nbsp;|&nbsp;
  Organisation: {org_label}
</footer>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Compliance Report – {org_label}</title>
  <style>{_BASE_CSS}</style>
</head>
<body>
<div class="page">
{cover}
{system_table}
{gap_section}
{risk_section}
{rec_section}
{inc_section}
{footer}
</div>
</body>
</html>"""

    return html


# ---------------------------------------------------------------------------
# generate_gap_analysis_csv
# ---------------------------------------------------------------------------

def generate_gap_analysis_csv(org_id: str, db: Session) -> bytes:
    """
    Generate a CSV file containing all compliance gaps for the organisation.

    Returns:
        CSV content as bytes (UTF-8 with BOM for Excel compatibility).
    """
    data = _fetch_org_data(org_id, db)
    checks = data["checks"]
    reg_map = data["reg_map"]
    system_map: Dict[str, AISystem] = {s.id: s for s in data["systems"]}

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Check ID",
        "AI System",
        "System Risk Tier",
        "Regulation",
        "Jurisdiction",
        "Status",
        "Priority",
        "Gap Description",
        "Remediation Steps",
        "Deadline",
        "Checked At",
    ])

    for c in sorted(checks, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.priority, 4)):
        reg = reg_map.get(c.regulation_id)
        system = system_map.get(c.ai_system_id)
        writer.writerow([
            c.id,
            system.name if system else c.ai_system_id,
            (system.risk_classification or "unclassified") if system else "N/A",
            reg.short_name if reg else c.regulation_id,
            reg.jurisdiction if reg else "N/A",
            c.status,
            c.priority,
            c.gap_description or "",
            c.remediation_steps or "",
            c.deadline.strftime("%Y-%m-%d") if c.deadline else "",
            c.checked_at.strftime("%Y-%m-%d %H:%M") if c.checked_at else "",
        ])

    # UTF-8 BOM for Excel compatibility
    return b"\xef\xbb\xbf" + output.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# generate_executive_summary
# ---------------------------------------------------------------------------

def generate_executive_summary(org_id: str, db: Session, org_name: Optional[str] = None) -> str:
    """
    Generate a concise executive summary HTML (1-page style).

    Returns:
        HTML string.
    """
    data = _fetch_org_data(org_id, db)
    systems = data["systems"]
    checks = data["checks"]
    incidents = data["incidents"]

    org_label = org_name or org_id
    report_date = datetime.utcnow().strftime("%B %d, %Y")
    overall_score = _compute_overall_score(checks)
    risk_dist = _risk_distribution(systems)

    compliant_count = sum(1 for c in checks if c.status == "compliant")
    non_compliant_count = sum(1 for c in checks if c.status == "non_compliant")
    critical_count = sum(1 for c in checks if c.priority == "critical" and c.status != "compliant")
    open_incidents = sum(1 for i in incidents if i.status not in ("resolved", "closed"))

    score_color = "#27ae60" if overall_score >= 75 else "#f39c12" if overall_score >= 50 else "#e74c3c"

    top_gaps = [
        c for c in sorted(checks, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.priority, 4))
        if c.status != "compliant" and c.gap_description
    ][:5]

    gap_bullets = "".join(
        f'<li><strong>[{c.priority.upper()}]</strong> {c.gap_description[:100]}...</li>'
        for c in top_gaps
    ) or "<li>No critical compliance gaps identified.</li>"

    risk_summary = ", ".join(
        f"{count} {tier}" for tier, count in risk_dist.items() if count > 0
    ) or "No systems classified"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Executive Summary – {org_label}</title>
  <style>
    {_BASE_CSS}
    .exec-header {{ background: linear-gradient(135deg, #1a252f 0%, #2c3e50 100%);
                    color: #fff; padding: 32px 40px; border-radius: 8px; margin-bottom: 28px; }}
    .exec-header h1 {{ color: #fff; font-size: 1.8em; margin: 0 0 4px; }}
    .exec-header .sub {{ color: #bdc3c7; font-size: 0.95em; }}
    .score-display {{ font-size: 3em; font-weight: 900; color: {score_color}; margin: 8px 0; }}
    .kpi-row {{ display: flex; gap: 14px; flex-wrap: wrap; margin: 20px 0; }}
    .kpi {{ background: #fff; border-radius: 8px; padding: 14px 18px;
             box-shadow: 0 2px 6px rgba(0,0,0,.08); flex: 1; min-width: 110px; text-align: center; }}
    .kpi .v {{ font-size: 2em; font-weight: bold; }}
    .kpi .l {{ font-size: 0.75em; color: #7f8c8d; text-transform: uppercase; }}
    ul {{ padding-left: 20px; }}
    li {{ margin: 6px 0; font-size: 0.9em; }}
  </style>
</head>
<body>
<div class="page">
  <div class="exec-header">
    <h1>Executive Compliance Summary</h1>
    <div class="sub">{org_label} &nbsp;|&nbsp; {report_date}</div>
    <div class="score-display">{overall_score:.1f}<span style="font-size:0.4em;color:#bdc3c7"> / 100</span></div>
    <div class="sub">Overall Compliance Score</div>
  </div>

  <div class="kpi-row">
    <div class="kpi"><div class="v">{len(systems)}</div><div class="l">AI Systems</div></div>
    <div class="kpi"><div class="v" style="color:#27ae60">{compliant_count}</div><div class="l">Compliant</div></div>
    <div class="kpi"><div class="v" style="color:#e74c3c">{non_compliant_count}</div><div class="l">Non-Compliant</div></div>
    <div class="kpi"><div class="v" style="color:#c0392b">{critical_count}</div><div class="l">Critical Gaps</div></div>
    <div class="kpi"><div class="v" style="color:#e67e22">{open_incidents}</div><div class="l">Open Incidents</div></div>
  </div>

  <h2>Risk Landscape</h2>
  <p>{risk_summary}</p>

  <h2>Top Compliance Gaps</h2>
  <ul>{gap_bullets}</ul>

  <h2>Key Recommendations</h2>
  <p>
    Focus remediation efforts on <strong>{critical_count} critical</strong> compliance gaps.
    {f"Address {open_incidents} open incident(s) promptly." if open_incidents else "No open incidents."}
    Review system risk classifications and ensure applicable regulations are mapped.
  </p>

  <footer>
    Adhi Compliance Platform &nbsp;|&nbsp; Executive Summary &nbsp;|&nbsp; {report_date}
  </footer>
</div>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# html_to_pdf
# ---------------------------------------------------------------------------

def html_to_pdf(html_string: str) -> bytes:
    """
    Convert an HTML string to PDF bytes.

    Attempts to use weasyprint first; falls back to reportlab plain-text
    rendering if weasyprint is not installed.

    Returns:
        PDF as bytes.
    """
    # Attempt weasyprint (full CSS support)
    try:
        from weasyprint import HTML  # type: ignore
        pdf_bytes: bytes = HTML(string=html_string).write_pdf()
        print("[ReportGenerator] PDF generated via weasyprint.")
        return pdf_bytes
    except ImportError:
        pass
    except Exception as exc:
        print(f"[ReportGenerator] weasyprint failed: {exc}. Falling back to reportlab.")

    # Fallback: reportlab plain-text PDF
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
        from reportlab.lib.units import cm  # type: ignore
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer  # type: ignore
        from reportlab.lib import colors  # type: ignore
        import re

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                                topMargin=2 * cm, bottomMargin=2 * cm)
        styles = getSampleStyleSheet()
        story = []

        # Strip HTML tags for plain-text fallback
        text = re.sub(r"<[^>]+>", " ", html_string)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"\s{2,}", " ", text)

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            style = styles["Normal"]
            story.append(Paragraph(line, style))
            story.append(Spacer(1, 2))

        doc.build(story)
        print("[ReportGenerator] PDF generated via reportlab (plain-text fallback).")
        return buf.getvalue()

    except ImportError:
        pass

    # Last resort: return HTML wrapped as a trivial "PDF" placeholder
    print("[ReportGenerator] Neither weasyprint nor reportlab available – returning raw HTML bytes.")
    return html_string.encode("utf-8")

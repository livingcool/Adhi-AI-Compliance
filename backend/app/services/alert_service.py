"""
Alert Service.

Sends compliance alerts via email (SMTP), Slack (webhook), and
Microsoft Teams (webhook). Configuration is loaded from environment
variables via app.config.
"""

import json
import smtplib
import urllib.request
import urllib.error
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
import os


# ---------------------------------------------------------------------------
# Alert type constants
# ---------------------------------------------------------------------------

ALERT_COMPLIANCE_DRIFT = "compliance_drift"
ALERT_DEADLINE_APPROACHING = "deadline_approaching"
ALERT_NEW_REGULATION = "new_regulation"
ALERT_INCIDENT_DETECTED = "incident_detected"
ALERT_AUDIT_FAILED = "audit_failed"

VALID_ALERT_TYPES = {
    ALERT_COMPLIANCE_DRIFT,
    ALERT_DEADLINE_APPROACHING,
    ALERT_NEW_REGULATION,
    ALERT_INCIDENT_DETECTED,
    ALERT_AUDIT_FAILED,
}

VALID_CHANNELS = {"email", "slack", "teams"}

# ---------------------------------------------------------------------------
# Severity icons and colours per alert type
# ---------------------------------------------------------------------------

_ALERT_META: Dict[str, Dict[str, str]] = {
    ALERT_COMPLIANCE_DRIFT: {
        "icon": "⚠️",
        "severity": "HIGH",
        "color": "#FF6B35",
        "title": "Compliance Drift Detected",
    },
    ALERT_DEADLINE_APPROACHING: {
        "icon": "⏰",
        "severity": "MEDIUM",
        "color": "#FFB347",
        "title": "Compliance Deadline Approaching",
    },
    ALERT_NEW_REGULATION: {
        "icon": "📋",
        "severity": "INFO",
        "color": "#4A90D9",
        "title": "New Regulation Published",
    },
    ALERT_INCIDENT_DETECTED: {
        "icon": "🚨",
        "severity": "CRITICAL",
        "color": "#D9534F",
        "title": "AI Incident Detected",
    },
    ALERT_AUDIT_FAILED: {
        "icon": "❌",
        "severity": "HIGH",
        "color": "#C0392B",
        "title": "Compliance Audit Failed",
    },
}


# ---------------------------------------------------------------------------
# format_alert
# ---------------------------------------------------------------------------

def format_alert(alert_type: str, data: Dict[str, Any]) -> str:
    """
    Return a human-readable formatted alert message with severity icon.

    Args:
        alert_type: One of the ALERT_* constants.
        data:       Contextual data dict included in the alert body.

    Returns:
        Plain-text formatted message string.
    """
    meta = _ALERT_META.get(alert_type, {"icon": "ℹ️", "severity": "INFO", "title": alert_type})
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"{meta['icon']} [{meta['severity']}] {meta['title']}",
        f"Timestamp: {timestamp}",
        "─" * 50,
    ]

    # Render data fields in a readable way
    for key, value in data.items():
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            lines.append(f"{label}:")
            for item in value:
                lines.append(f"  • {item}")
        else:
            lines.append(f"{label}: {value}")

    lines.append("─" * 50)
    lines.append("Adhi Compliance Platform | Automated Alert")
    return "\n".join(lines)


def _format_slack_payload(alert_type: str, message: str, data: Dict[str, Any]) -> Dict:
    """Build a Slack Block Kit message payload."""
    meta = _ALERT_META.get(alert_type, {"icon": "ℹ️", "severity": "INFO", "color": "#888888", "title": alert_type})
    return {
        "attachments": [
            {
                "color": meta["color"],
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{meta['icon']} {meta['title']} [{meta['severity']}]",
                        },
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": message},
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Adhi Compliance* | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                            }
                        ],
                    },
                ],
            }
        ]
    }


def _format_teams_payload(alert_type: str, message: str) -> Dict:
    """Build a Microsoft Teams Adaptive Card payload."""
    meta = _ALERT_META.get(alert_type, {"icon": "ℹ️", "severity": "INFO", "color": "default", "title": alert_type})
    color_map = {"CRITICAL": "attention", "HIGH": "warning", "MEDIUM": "accent", "INFO": "good"}
    card_color = color_map.get(meta["severity"], "default")

    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"{meta['icon']} {meta['title']}",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": card_color,
                        },
                        {
                            "type": "TextBlock",
                            "text": message.replace("\n", "\n\n"),
                            "wrap": True,
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Adhi Compliance | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                            "isSubtle": True,
                            "size": "Small",
                        },
                    ],
                },
            }
        ],
    }


# ---------------------------------------------------------------------------
# Channel senders
# ---------------------------------------------------------------------------

def _send_slack(message: str, alert_type: str, data: Dict[str, Any]) -> bool:
    """POST to Slack incoming webhook. Returns True on success."""
    webhook_url = os.environ.get("ALERT_SLACK_WEBHOOK", "")
    if not webhook_url:
        print("[AlertService] Slack alert skipped – ALERT_SLACK_WEBHOOK not configured.")
        return False

    payload = _format_slack_payload(alert_type, message, data)
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            success = resp.status == 200
            if not success:
                print(f"[AlertService] Slack webhook returned HTTP {resp.status}.")
            return success
    except urllib.error.URLError as exc:
        print(f"[AlertService] Slack webhook error: {exc}")
        return False


def _send_teams(message: str, alert_type: str) -> bool:
    """POST to Microsoft Teams incoming webhook. Returns True on success."""
    webhook_url = os.environ.get("ALERT_TEAMS_WEBHOOK", "")
    if not webhook_url:
        print("[AlertService] Teams alert skipped – ALERT_TEAMS_WEBHOOK not configured.")
        return False

    payload = _format_teams_payload(alert_type, message)
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            success = resp.status in (200, 202)
            if not success:
                print(f"[AlertService] Teams webhook returned HTTP {resp.status}.")
            return success
    except urllib.error.URLError as exc:
        print(f"[AlertService] Teams webhook error: {exc}")
        return False


def _send_email(
    message: str,
    alert_type: str,
    recipients: List[str],
) -> bool:
    """
    Send alert via SMTP email. Returns True on success.

    Expected env vars:
        ALERT_EMAIL_SMTP   – smtp://user:pass@host:port  (or host:port for no-auth)
        ALERT_EMAIL_FROM   – sender address (default: alerts@adhi-compliance.ai)
    """
    smtp_dsn = os.environ.get("ALERT_EMAIL_SMTP", "")
    if not smtp_dsn:
        print("[AlertService] Email alert skipped – ALERT_EMAIL_SMTP not configured.")
        return False
    if not recipients:
        print("[AlertService] Email alert skipped – no recipients provided.")
        return False

    from_addr = os.environ.get("ALERT_EMAIL_FROM", "alerts@adhi-compliance.ai")
    meta = _ALERT_META.get(alert_type, {"title": alert_type, "severity": "INFO"})
    subject = f"[{meta['severity']}] {meta['title']} – Adhi Compliance"

    # Parse SMTP DSN: smtp://user:pass@host:port  or  host:port
    host = "localhost"
    port = 587
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None

    try:
        dsn = smtp_dsn
        if dsn.startswith("smtp://"):
            dsn = dsn[7:]
        if "@" in dsn:
            creds, hostport = dsn.rsplit("@", 1)
            smtp_user, smtp_pass = creds.split(":", 1)
        else:
            hostport = dsn
        host_part, *port_part = hostport.split(":")
        host = host_part or "localhost"
        port = int(port_part[0]) if port_part else 587
    except Exception as exc:
        print(f"[AlertService] Failed to parse ALERT_EMAIL_SMTP DSN: {exc}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(message, "plain"))

    # Simple HTML version
    html_body = f"<pre style='font-family:monospace'>{message}</pre>"
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, recipients, msg.as_string())
        print(f"[AlertService] Email sent to {len(recipients)} recipient(s).")
        return True
    except Exception as exc:
        print(f"[AlertService] Email send failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_alert(
    alert_type: str,
    message: str,
    channel: str,
    recipients: Optional[List[str]] = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Dispatch an alert to the specified channel.

    Args:
        alert_type:  One of the ALERT_* constants (e.g. 'compliance_drift').
        message:     Human-readable alert body text.
        channel:     Delivery channel: 'email', 'slack', or 'teams'.
        recipients:  List of email addresses (only used when channel='email').
        data:        Extra context dict (used for Slack block formatting).

    Returns:
        {"success": bool, "channel": str, "alert_type": str, "sent_at": str}
    """
    if alert_type not in VALID_ALERT_TYPES:
        print(f"[AlertService] Unknown alert_type '{alert_type}'. Defaulting to info.")

    data = data or {}
    recipients = recipients or []
    success = False

    if channel == "slack":
        success = _send_slack(message, alert_type, data)
    elif channel == "teams":
        success = _send_teams(message, alert_type)
    elif channel == "email":
        success = _send_email(message, alert_type, recipients)
    else:
        print(f"[AlertService] Unknown channel '{channel}'. No alert sent.")

    result = {
        "success": success,
        "channel": channel,
        "alert_type": alert_type,
        "sent_at": datetime.utcnow().isoformat(),
    }
    print(
        f"[AlertService] alert_type={alert_type} channel={channel} "
        f"success={success} recipients={len(recipients)}"
    )
    return result


def send_alert_all_channels(
    alert_type: str,
    data: Dict[str, Any],
    recipients: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience wrapper: format the alert and send to all configured channels.

    Returns a list of send_alert result dicts (one per attempted channel).
    """
    message = format_alert(alert_type, data)
    results = []
    for channel in ("slack", "teams", "email"):
        result = send_alert(
            alert_type=alert_type,
            message=message,
            channel=channel,
            recipients=recipients,
            data=data,
        )
        results.append(result)
    return results

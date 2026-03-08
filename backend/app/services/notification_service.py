"""
Unified notification service for Adhi Compliance.

Supports four notification channels:
  1. Email via SMTP
  2. Slack via incoming webhook
  3. Microsoft Teams via incoming webhook
  4. In-app (stored in the `notifications` DB table)

Usage:
    from app.services.notification_service import NotificationService
    from app.store.models import get_db_session

    svc = NotificationService(db)
    svc.notify(
        user_id="...",
        org_id="...",
        title="Compliance Deadline Approaching",
        message="EU AI Act deadline in 7 days for System XYZ",
        notif_type="compliance",
        channels=["in_app", "email", "slack"],
        email_to="user@example.com",
    )
"""

from __future__ import annotations

import logging
import smtplib
import ssl
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from sqlalchemy.orm import Session

from app.store.models import Notification

logger = logging.getLogger("adhi_compliance.notifications")


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------

class NotificationService:
    """
    Unified notification dispatcher.

    Instantiate once per request with an active DB session.
    Channel credentials are loaded from app settings on first use.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # High-level API
    # ------------------------------------------------------------------

    def notify(
        self,
        user_id: str,
        org_id: str,
        title: str,
        message: str,
        notif_type: str = "system",
        channels: Optional[List[str]] = None,
        email_to: Optional[str] = None,
    ) -> Notification:
        """
        Send a notification through one or more channels and persist in-app record.

        Args:
            user_id:     Recipient user ID (for in-app notifications).
            org_id:      Organisation ID.
            title:       Short notification title.
            message:     Full notification body.
            notif_type:  Category: 'compliance' | 'incident' | 'system' | 'alert'.
            channels:    List of channels to use. Defaults to ['in_app'].
                         Valid values: 'in_app', 'email', 'slack', 'teams'.
            email_to:    Email address (required when 'email' is in channels).

        Returns:
            The persisted Notification DB record.
        """
        if channels is None:
            channels = ["in_app"]

        notif = self.create_in_app(user_id, org_id, title, message, notif_type)

        for channel in channels:
            if channel == "in_app":
                continue  # already created above
            elif channel == "email" and email_to:
                self._send_email_safe(email_to, title, message)
            elif channel == "slack":
                self._send_slack_safe(f"*{title}*\n{message}")
            elif channel == "teams":
                self._send_teams_safe(title, message)

        return notif

    # ------------------------------------------------------------------
    # In-app notifications
    # ------------------------------------------------------------------

    def create_in_app(
        self,
        user_id: str,
        org_id: str,
        title: str,
        message: str,
        notif_type: str = "system",
    ) -> Notification:
        """Persist a new in-app notification record."""
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            org_id=org_id,
            title=title,
            message=message,
            type=notif_type,
            read=False,
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def get_for_user(
        self,
        user_id: str,
        org_id: str,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Notification]:
        """Retrieve notifications for a user, newest first."""
        q = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.org_id == org_id)
        )
        if unread_only:
            q = q.filter(Notification.read == False)
        return q.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def mark_read(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """Mark a single notification as read. Returns None if not found/owned."""
        notif = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if not notif:
            return None
        notif.read = True
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def mark_all_read(self, user_id: str, org_id: str) -> int:
        """Mark all unread notifications for a user as read. Returns count updated."""
        updated = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.org_id == org_id,
                Notification.read == False,
            )
            .all()
        )
        for n in updated:
            n.read = True
        self.db.commit()
        return len(updated)

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email via SMTP.

        Reads SMTP DSN from settings.ALERT_EMAIL_SMTP.
        DSN format: smtp://user:pass@host:port  or  smtps://...

        Returns True on success, False on failure.
        """
        from app.config import settings

        smtp_dsn = settings.ALERT_EMAIL_SMTP
        if not smtp_dsn:
            logger.debug("Email notification skipped: ALERT_EMAIL_SMTP not configured.")
            return False

        try:
            parsed = urlparse(smtp_dsn)
            host = parsed.hostname or "localhost"
            port = parsed.port or 587
            user = parsed.username or ""
            password = parsed.password or ""
            use_ssl = parsed.scheme == "smtps"

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.ALERT_EMAIL_FROM
            msg["To"] = to
            msg.attach(MIMEText(body, "plain"))

            if use_ssl:
                ctx = ssl.create_default_context()
                with smtplib.SMTP_SSL(host, port, context=ctx) as server:
                    if user:
                        server.login(user, password)
                    server.sendmail(settings.ALERT_EMAIL_FROM, [to], msg.as_string())
            else:
                with smtplib.SMTP(host, port) as server:
                    server.ehlo()
                    server.starttls()
                    if user:
                        server.login(user, password)
                    server.sendmail(settings.ALERT_EMAIL_FROM, [to], msg.as_string())

            logger.info("Email sent to %s: %s", to, subject)
            return True

        except Exception as exc:
            logger.warning("Email send failed to %s: %s", to, exc)
            return False

    # ------------------------------------------------------------------
    # Slack
    # ------------------------------------------------------------------

    def send_slack(self, text: str, webhook_url: Optional[str] = None) -> bool:
        """
        Post a message to Slack via incoming webhook.

        Args:
            text:        Plain-text message (supports Slack mrkdwn).
            webhook_url: Override the webhook URL from settings.

        Returns True on success, False on failure.
        """
        from app.config import settings

        url = webhook_url or settings.ALERT_SLACK_WEBHOOK
        if not url:
            logger.debug("Slack notification skipped: ALERT_SLACK_WEBHOOK not configured.")
            return False

        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text},
                }
            ]
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Slack notification sent.")
            return True
        except Exception as exc:
            logger.warning("Slack send failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Microsoft Teams
    # ------------------------------------------------------------------

    def send_teams(self, title: str, text: str, webhook_url: Optional[str] = None) -> bool:
        """
        Post an Adaptive Card message to Microsoft Teams via incoming webhook.

        Returns True on success, False on failure.
        """
        from app.config import settings

        url = webhook_url or settings.ALERT_TEAMS_WEBHOOK
        if not url:
            logger.debug("Teams notification skipped: ALERT_TEAMS_WEBHOOK not configured.")
            return False

        payload: Dict[str, Any] = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {"type": "TextBlock", "size": "Medium", "weight": "Bolder", "text": title},
                            {"type": "TextBlock", "text": text, "wrap": True},
                        ],
                    },
                }
            ],
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Teams notification sent.")
            return True
        except Exception as exc:
            logger.warning("Teams send failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Internal safe wrappers (never raise)
    # ------------------------------------------------------------------

    def _send_email_safe(self, to: str, subject: str, body: str) -> None:
        try:
            self.send_email(to, subject, body)
        except Exception as exc:
            logger.warning("Email notification error: %s", exc)

    def _send_slack_safe(self, text: str) -> None:
        try:
            self.send_slack(text)
        except Exception as exc:
            logger.warning("Slack notification error: %s", exc)

    def _send_teams_safe(self, title: str, text: str) -> None:
        try:
            self.send_teams(title, text)
        except Exception as exc:
            logger.warning("Teams notification error: %s", exc)


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_notification_service(db: Session = None) -> NotificationService:
    """Return a NotificationService bound to the given session."""
    return NotificationService(db)

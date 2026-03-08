"""
Compliance Monitor Service.

Orchestrates periodic compliance scanning across all AI systems,
detects compliance drift, and surfaces upcoming deadlines.

Alert triggers:
  - After scan_all_systems(): non-compliant results → send_alert_all_channels
  - get_upcoming_deadlines(): deadlines within 7/14/30 days trigger deadline alerts
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.store.models import AISystem, ComplianceCheck, Regulation
from app.services.compliance_checker import check_compliance
from app.services.risk_classifier import _get_applicable_regulations

logger = logging.getLogger("adhi.compliance_monitor")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _log_audit(action: str, details: str, org_id: str) -> Dict[str, Any]:
    """Creates a structured audit trail entry (logged via logger)."""
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details,
        "org_id": org_id,
    }
    logger.info(
        "audit_trail",
        extra={"action": action, "org_id": org_id, "details": details[:120]},
    )
    return entry


def _get_applicable_regulation_ids(system: AISystem, db: Session) -> List[str]:
    """
    Derive the list of regulation IDs applicable to a system based on its
    risk tier and deployment regions (using the same logic as the classifier).
    """
    risk_tier = system.risk_classification or "minimal"
    regions = system.deployment_regions or []
    regs = _get_applicable_regulations(db=db, risk_tier=risk_tier, deployment_regions=regions)
    return [r["id"] for r in regs]


# ---------------------------------------------------------------------------
# ComplianceMonitor class
# ---------------------------------------------------------------------------

class ComplianceMonitor:
    """
    Orchestrates compliance scanning, drift detection, and deadline surfacing.
    All methods accept a SQLAlchemy Session so they can be called from
    FastAPI routes (session-per-request) or scheduled tasks.
    """

    # ------------------------------------------------------------------
    # scan_all_systems
    # ------------------------------------------------------------------

    def scan_all_systems(
        self,
        db: Session,
        org_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Iterate all AISystem records (optionally filtered by org_id),
        run compliance_checker against each applicable regulation,
        and return a summary of what was scanned.

        Returns:
            {
                "scanned_systems": int,
                "checks_created": int,
                "errors": [{"system_id": ..., "error": ...}],
                "audit_entries": [...],
            }
        """
        query = db.query(AISystem)
        if org_id:
            query = query.filter(AISystem.org_id == org_id)
        systems = query.all()

        scanned = 0
        checks_created = 0
        errors: List[Dict[str, Any]] = []
        audit_entries: List[Dict[str, Any]] = []

        for system in systems:
            try:
                reg_ids = _get_applicable_regulation_ids(system, db)
                if not reg_ids:
                    audit_entries.append(_log_audit(
                        action="scan_skipped",
                        details=f"System '{system.name}' ({system.id}) – no applicable regulations found.",
                        org_id=system.org_id,
                    ))
                    continue

                for reg_id in reg_ids:
                    try:
                        check_compliance(
                            ai_system_id=system.id,
                            regulation_id=reg_id,
                            org_id=system.org_id,
                            db=db,
                        )
                        checks_created += 1
                    except Exception as exc:
                        errors.append({"system_id": system.id, "regulation_id": reg_id, "error": str(exc)})
                        print(f"[ComplianceMonitor] Check failed system={system.id} reg={reg_id}: {exc}")

                scanned += 1
                audit_entries.append(_log_audit(
                    action="system_scanned",
                    details=f"System '{system.name}' scanned against {len(reg_ids)} regulation(s).",
                    org_id=system.org_id,
                ))

            except Exception as exc:
                errors.append({"system_id": system.id, "error": str(exc)})
                print(f"[ComplianceMonitor] System scan failed system={system.id}: {exc}")

        summary = {
            "scanned_systems": scanned,
            "checks_created": checks_created,
            "errors": errors,
            "audit_entries": audit_entries,
            "scan_timestamp": datetime.utcnow().isoformat(),
        }
        logger.info(
            "scan_all_systems_complete",
            extra={"scanned": scanned, "checks": checks_created, "errors": len(errors)},
        )

        # --- Alert: non-compliant results after scan ---
        self._alert_non_compliant(db=db, org_id=org_id)

        return summary

    # ------------------------------------------------------------------
    # check_regulation_updates
    # ------------------------------------------------------------------

    def check_regulation_updates(self) -> Dict[str, Any]:
        """
        Placeholder for future external API integration to detect new
        or amended regulations (e.g. EUR-Lex, Federal Register APIs).

        Returns a stub response indicating no updates detected.
        """
        print("[ComplianceMonitor] check_regulation_updates – placeholder, no external API configured.")
        return {
            "status": "placeholder",
            "message": (
                "Regulation update check not yet integrated with external APIs. "
                "Configure REGULATION_UPDATE_API_URL to enable."
            ),
            "checked_at": datetime.utcnow().isoformat(),
            "new_regulations": [],
            "amended_regulations": [],
        }

    # ------------------------------------------------------------------
    # detect_compliance_drift
    # ------------------------------------------------------------------

    def detect_compliance_drift(
        self,
        system_id: str,
        db: Session,
    ) -> Dict[str, Any]:
        """
        Compare the two most recent ComplianceCheck records per regulation
        for the given system. Flag as 'drifted' if score/status worsened.

        Score mapping: compliant=100, partial=50, pending=25, non_compliant=0.

        Returns:
            {
                "system_id": str,
                "drift_detected": bool,
                "drifted_regulations": [...],
                "stable_regulations": [...],
                "checked_at": str,
            }
        """
        _STATUS_SCORE = {
            "compliant": 100,
            "partial": 50,
            "pending": 25,
            "non_compliant": 0,
        }

        # Fetch all regulation IDs that have checks for this system
        rows = (
            db.query(ComplianceCheck.regulation_id)
            .filter(ComplianceCheck.ai_system_id == system_id)
            .distinct()
            .all()
        )
        reg_ids = [r[0] for r in rows]

        drifted: List[Dict[str, Any]] = []
        stable: List[Dict[str, Any]] = []

        for reg_id in reg_ids:
            # Get the two most recent checks for this system + regulation
            checks = (
                db.query(ComplianceCheck)
                .filter(
                    ComplianceCheck.ai_system_id == system_id,
                    ComplianceCheck.regulation_id == reg_id,
                )
                .order_by(ComplianceCheck.checked_at.desc())
                .limit(2)
                .all()
            )

            if len(checks) < 2:
                # Not enough history to compare
                stable.append({
                    "regulation_id": reg_id,
                    "note": "insufficient_history",
                    "latest_status": checks[0].status if checks else None,
                })
                continue

            latest, previous = checks[0], checks[1]
            latest_score = _STATUS_SCORE.get(latest.status, 0)
            prev_score = _STATUS_SCORE.get(previous.status, 0)
            delta = latest_score - prev_score

            if delta < 0:
                drifted.append({
                    "regulation_id": reg_id,
                    "previous_status": previous.status,
                    "current_status": latest.status,
                    "score_delta": delta,
                    "previous_checked_at": previous.checked_at.isoformat(),
                    "current_checked_at": latest.checked_at.isoformat(),
                })
            else:
                stable.append({
                    "regulation_id": reg_id,
                    "previous_status": previous.status,
                    "current_status": latest.status,
                    "score_delta": delta,
                })

        result = {
            "system_id": system_id,
            "drift_detected": len(drifted) > 0,
            "drifted_regulations": drifted,
            "stable_regulations": stable,
            "checked_at": datetime.utcnow().isoformat(),
        }

        if drifted:
            print(
                f"[ComplianceMonitor] DRIFT DETECTED – system={system_id}, "
                f"{len(drifted)} regulation(s) worsened."
            )
        return result

    # ------------------------------------------------------------------
    # get_upcoming_deadlines
    # ------------------------------------------------------------------

    def get_upcoming_deadlines(
        self,
        db: Session,
        days: int = 30,
        org_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query ComplianceCheck records whose deadline falls within the next
        `days` calendar days.

        Returns a list of deadline items sorted by soonest deadline first.
        """
        now = datetime.utcnow()
        cutoff = now + timedelta(days=days)

        query = db.query(ComplianceCheck).filter(
            ComplianceCheck.deadline.isnot(None),
            ComplianceCheck.deadline >= now,
            ComplianceCheck.deadline <= cutoff,
        )
        if org_id:
            query = query.filter(ComplianceCheck.org_id == org_id)

        checks = query.order_by(ComplianceCheck.deadline.asc()).all()

        results = []
        for c in checks:
            days_remaining = (c.deadline - now).days
            results.append({
                "check_id": c.id,
                "ai_system_id": c.ai_system_id,
                "regulation_id": c.regulation_id,
                "status": c.status,
                "priority": c.priority,
                "deadline": c.deadline.isoformat(),
                "days_remaining": days_remaining,
                "gap_description": c.gap_description,
                "org_id": c.org_id,
            })

        logger.info(
            "get_upcoming_deadlines",
            extra={"count": len(results), "days": days, "org_id": org_id},
        )

        # --- Alert: deadlines within threshold windows ---
        self._alert_deadlines(results)

        return results

    # ------------------------------------------------------------------
    # _alert_non_compliant  (internal)
    # ------------------------------------------------------------------

    def _alert_non_compliant(
        self,
        db: Session,
        org_id: Optional[str] = None,
    ) -> None:
        """
        Query the most recent non-compliant ComplianceCheck records and send
        an alert for each one to all configured channels.
        Called automatically after scan_all_systems().
        """
        try:
            from app.services.alert_service import (
                ALERT_COMPLIANCE_DRIFT,
                format_alert,
                send_alert_all_channels,
            )

            q = db.query(ComplianceCheck).filter(
                ComplianceCheck.status == "non_compliant"
            )
            if org_id:
                q = q.filter(ComplianceCheck.org_id == org_id)

            non_compliant = q.order_by(ComplianceCheck.checked_at.desc()).limit(20).all()
            if not non_compliant:
                return

            for check in non_compliant:
                data = {
                    "system_id": check.ai_system_id,
                    "regulation_id": check.regulation_id,
                    "priority": check.priority,
                    "gap": (check.gap_description or "")[:200],
                    "org_id": check.org_id,
                    "checked_at": check.checked_at.isoformat() if check.checked_at else "N/A",
                }
                send_alert_all_channels(
                    alert_type=ALERT_COMPLIANCE_DRIFT,
                    data=data,
                )
        except Exception as exc:
            logger.error("alert_non_compliant_failed", extra={"error": str(exc)})

    # ------------------------------------------------------------------
    # _alert_deadlines  (internal)
    # ------------------------------------------------------------------

    def _alert_deadlines(self, deadlines: List[Dict[str, Any]]) -> None:
        """
        Trigger alerts for deadlines falling within 7, 14, or 30 days.
        Called automatically after get_upcoming_deadlines().
        """
        try:
            from app.services.alert_service import (
                ALERT_DEADLINE_APPROACHING,
                send_alert_all_channels,
            )

            thresholds = [7, 14, 30]

            for item in deadlines:
                days_remaining = item.get("days_remaining", 999)
                # Only alert if the deadline falls inside one of the windows
                if days_remaining <= max(thresholds):
                    data = {
                        "check_id": item["check_id"],
                        "ai_system_id": item["ai_system_id"],
                        "regulation_id": item["regulation_id"],
                        "days_remaining": days_remaining,
                        "deadline": item["deadline"],
                        "status": item["status"],
                        "priority": item["priority"],
                        "org_id": item["org_id"],
                    }
                    send_alert_all_channels(
                        alert_type=ALERT_DEADLINE_APPROACHING,
                        data=data,
                    )
        except Exception as exc:
            logger.error("alert_deadlines_failed", extra={"error": str(exc)})


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

compliance_monitor = ComplianceMonitor()

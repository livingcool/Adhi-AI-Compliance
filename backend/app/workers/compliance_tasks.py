"""
Compliance Celery Tasks.

All heavy compliance operations are dispatched as background tasks so that
HTTP route handlers return immediately with a task_id.
"""

import logging
from typing import Optional

from app.workers.celery_app import celery_app

logger = logging.getLogger("adhi.celery")


# ---------------------------------------------------------------------------
# task_run_compliance_check
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="compliance.run_compliance_check", max_retries=2)
def task_run_compliance_check(self, system_id: str, regulation_id: str, org_id: str) -> dict:
    """
    Run a RAG-based compliance check for a single AI system against a regulation.
    Persists a ComplianceCheck row and returns its summary.
    """
    from app.store.metadata_store import SessionLocal
    from app.services.compliance_checker import check_compliance

    logger.info(
        "task_run_compliance_check.started",
        extra={"system_id": system_id, "regulation_id": regulation_id, "org_id": org_id},
    )
    db = SessionLocal()
    try:
        check = check_compliance(
            ai_system_id=system_id,
            regulation_id=regulation_id,
            org_id=org_id,
            db=db,
        )
        return {
            "check_id": check.id,
            "status": check.status,
            "priority": check.priority,
            "gap_description": check.gap_description,
        }
    except Exception as exc:
        logger.error("task_run_compliance_check.failed", extra={"error": str(exc)})
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# task_generate_report
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="compliance.generate_report")
def task_generate_report(
    self,
    org_id: str,
    report_type: str = "html",
    org_name: Optional[str] = None,
) -> dict:
    """
    Generate a compliance report for an organisation.

    report_type: 'html' | 'executive_summary' | 'csv'
    Returns dict with keys: type, content (string).
    """
    from app.store.metadata_store import SessionLocal
    from app.services.report_generator import (
        generate_compliance_report,
        generate_executive_summary,
        generate_gap_analysis_csv,
    )

    logger.info(
        "task_generate_report.started",
        extra={"org_id": org_id, "report_type": report_type},
    )
    db = SessionLocal()
    try:
        if report_type == "executive_summary":
            content = generate_executive_summary(org_id, db, org_name)
            return {"type": "html", "content": content}
        elif report_type == "csv":
            raw = generate_gap_analysis_csv(org_id, db)
            return {"type": "csv", "content": raw.decode("utf-8", errors="replace")}
        else:
            content = generate_compliance_report(org_id, db, org_name)
            return {"type": "html", "content": content}
    except Exception as exc:
        logger.error("task_generate_report.failed", extra={"error": str(exc)})
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# task_run_bias_audit
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="compliance.run_bias_audit")
def task_run_bias_audit(
    self,
    system_id: str,
    org_id: str,
    file_path: str,
    file_type: str = "csv",
    dataset_description: str = "",
) -> dict:
    """
    Run statistical bias audit on a saved dataset file.
    Persists a BiasAudit row and returns its summary.
    """
    import uuid
    from dataclasses import asdict

    from app.store.metadata_store import SessionLocal
    from app.services.bias_auditor import analyze_bias
    from app.store.models import BiasAudit

    logger.info("task_run_bias_audit.started", extra={"system_id": system_id, "file_path": file_path})
    db = SessionLocal()
    try:
        with open(file_path, "rb") as fh:
            content = fh.read()

        result = analyze_bias(content, file_type)

        findings = {
            "summary_findings": result.summary_findings,
            "summary_recommendations": result.summary_recommendations,
            "per_attribute": [asdict(m) for m in result.per_attribute],
            "dataset_row_count": result.dataset_row_count,
            "dataset_column_count": result.dataset_column_count,
            "protected_attributes_analyzed": result.protected_attributes_analyzed,
            "raw_details": result.raw_details,
        }

        audit = BiasAudit(
            id=str(uuid.uuid4()),
            ai_system_id=system_id,
            org_id=org_id,
            dataset_description=dataset_description or file_path,
            demographic_parity_score=result.demographic_parity_score,
            disparate_impact_ratio=result.disparate_impact_ratio,
            overall_status=result.overall_status,
            findings=findings,
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return {"audit_id": audit.id, "overall_status": audit.overall_status}
    except Exception as exc:
        logger.error("task_run_bias_audit.failed", extra={"error": str(exc)})
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# task_scan_all_systems
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="compliance.scan_all_systems")
def task_scan_all_systems(self, org_id: Optional[str] = None) -> dict:
    """
    Run a full compliance scan across all AI systems (optionally filtered by org_id).
    Triggered periodically by Celery Beat.
    """
    from app.store.metadata_store import SessionLocal
    from app.services.compliance_monitor import compliance_monitor

    logger.info("task_scan_all_systems.started", extra={"org_id": org_id})
    db = SessionLocal()
    try:
        result = compliance_monitor.scan_all_systems(db=db, org_id=org_id)
        logger.info(
            "task_scan_all_systems.done",
            extra={
                "scanned": result.get("scanned_systems"),
                "checks": result.get("checks_created"),
                "errors": len(result.get("errors", [])),
            },
        )
        return result
    except Exception as exc:
        logger.error("task_scan_all_systems.failed", extra={"error": str(exc)})
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# task_generate_model_card
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="compliance.generate_model_card")
def task_generate_model_card(self, system_id: str, org_id: str) -> dict:
    """
    Generate and persist an EU AI Act Article 13-aligned model card for an AI system.
    """
    import uuid

    from app.store.metadata_store import SessionLocal
    from app.services.model_card_generator import generate_model_card
    from app.store.models import AISystem, BiasAudit, ComplianceCheck, ModelCard

    logger.info("task_generate_model_card.started", extra={"system_id": system_id})
    db = SessionLocal()
    try:
        system = db.query(AISystem).filter(AISystem.id == system_id).first()
        if not system:
            raise ValueError(f"AISystem '{system_id}' not found")

        bias_audits = (
            db.query(BiasAudit)
            .filter(BiasAudit.ai_system_id == system_id)
            .order_by(BiasAudit.audit_date.desc())
            .all()
        )
        compliance_checks = (
            db.query(ComplianceCheck)
            .filter(ComplianceCheck.ai_system_id == system_id)
            .all()
        )

        card_data = generate_model_card(system, bias_audits, compliance_checks)

        card = ModelCard(
            id=str(uuid.uuid4()),
            ai_system_id=system_id,
            org_id=org_id,
            content=card_data,
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        return {"card_id": card.id, "system_id": system_id}
    except Exception as exc:
        logger.error("task_generate_model_card.failed", extra={"error": str(exc)})
        raise
    finally:
        db.close()

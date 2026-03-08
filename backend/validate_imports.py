#!/usr/bin/env python3
"""
Import validation script — tests every Python module in the app/ directory.
Prints OK or FAIL with full traceback for each module.
"""
import sys
import traceback
import importlib

MODULES_TO_TEST = [
    # Core
    "app.config",
    "app.store.metadata_store",
    "app.store.models",
    "app.store.supabase_client",
    "app.store.vector_store",
    # Core utilities
    "app.core.exceptions",
    "app.core.logging",
    "app.core.pagination",
    # Middleware
    "app.middleware.auth",
    "app.middleware.error_handler",
    # Services
    "app.services.alert_service",
    "app.services.audit_service",
    "app.services.bias_auditor",
    "app.services.compliance_checker",
    "app.services.compliance_monitor",
    "app.services.embedder",
    "app.services.model_card_generator",
    "app.services.notification_service",
    "app.services.normalization_service",
    "app.services.pdf_processor",
    "app.services.regulation_embedder",
    "app.services.regulation_loader",
    "app.services.regulation_updater",
    "app.services.report_generator",
    "app.services.risk_classifier",
    "app.services.text_chunker",
    "app.services.usage_logger",
    # Repositories
    "app.repositories.base",
    "app.repositories.ai_system_repo",
    "app.repositories.bias_audit_repo",
    "app.repositories.compliance_repo",
    "app.repositories.incident_repo",
    "app.repositories.model_card_repo",
    "app.repositories.regulation_repo",
    "app.repositories.user_repo",
    # LLM
    "app.llm.prompt_templates",
    "app.llm.answer_generator",
    "app.llm.hf_answer_generator",
    # Retrieval
    "app.retrieval.retriever",
    "app.retrieval.llm_rewriter",
    # Workers
    "app.workers.celery_app",
    "app.workers.compliance_tasks",
    # API routes
    "app.api.schemas",
    "app.api.compliance_schemas",
    "app.api.routes_auth",
    "app.api.routes_ai_systems",
    "app.api.routes_bias",
    "app.api.routes_company",
    "app.api.routes_compliance",
    "app.api.routes_dashboard",
    "app.api.routes_incidents",
    "app.api.routes_ingest",
    "app.api.routes_model_cards",
    "app.api.routes_monitoring",
    "app.api.routes_notifications",
    "app.api.routes_org",
    "app.api.routes_query",
    "app.api.routes_regulation_mgmt",
    "app.api.routes_regulations",
    "app.api.routes_reports",
    "app.api.routes_seed",
    "app.api.routes_static",
    "app.api.routes_task",
    "app.api.routes_tasks",
    # Main app
    "app.main",
]

ok = 0
fail = 0
failures = []

for mod in MODULES_TO_TEST:
    try:
        importlib.import_module(mod)
        print(f"  OK  {mod}")
        ok += 1
    except Exception as e:
        tb = traceback.format_exc()
        print(f"FAIL  {mod}")
        print(f"      Error: {e}")
        print(f"      Traceback:\n{tb}")
        fail += 1
        failures.append((mod, str(e), tb))

print(f"\n{'='*60}")
print(f"Results: {ok} OK, {fail} FAILED")
if failures:
    print("\nFAILED MODULES:")
    for mod, err, _ in failures:
        print(f"  - {mod}: {err}")
sys.exit(0 if fail == 0 else 1)

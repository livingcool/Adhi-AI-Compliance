from fastapi import FastAPI, Depends
from app.config import Settings, get_settings, settings
from app.api import routes_ingest, routes_task, routes_query, routes_static, routes_org
from app.api import (
    routes_company,
    routes_ai_systems,
    routes_compliance,
    routes_regulations,
    routes_incidents,
    routes_bias,
    routes_seed,
    routes_model_cards,
    routes_reports,
    routes_monitoring,
    routes_dashboard,
    routes_auth,
    routes_tasks,
    routes_regulation_mgmt,
    routes_notifications,
)
from app.middleware.error_handler import register_error_handlers
from app.core.logging import configure_logging, RequestLoggingMiddleware

from fastapi.middleware.cors import CORSMiddleware

# --- Configure structured JSON logging at startup ---
configure_logging(log_level=settings.LOG_LEVEL.value)

# Create the FastAPI app instance
app = FastAPI(
    title="Adhi Compliance",
    description="AI Compliance Platform — ingestion, RAG, and regulatory compliance APIs.",
    version="1.0.0",
)

# --- Request logging middleware ---
app.add_middleware(RequestLoggingMiddleware)

# --- Configure CORS (restricted to configured origins) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Register global error handlers ---
register_error_handlers(app)

# NOTE: Database tables are managed by Alembic migrations.
# Run `alembic upgrade head` before starting the server for the first time.

# --- Include API Routers ---
app.include_router(
    routes_ingest.router,
    prefix="/api/v1",
    tags=["1. Ingestion"]
)
app.include_router(
    routes_task.router,
    prefix="/api/v1",
    tags=["2. Task Status"]
)
app.include_router(
    routes_query.router,
    prefix="/api/v1",    tags=["3. Query"]
)
app.include_router(
    routes_org.router,
    prefix="/api/v1",
    tags=["4. Organizations"]
)
app.include_router(
    routes_static.router,
    tags=["5. Static Files"]
)

# --- Compliance Routers ---
app.include_router(
    routes_company.router,
    prefix="/api/v1",
    tags=["6. Company Profiles"]
)
app.include_router(
    routes_ai_systems.router,
    prefix="/api/v1",
    tags=["7. AI Systems"]
)
app.include_router(
    routes_compliance.router,
    prefix="/api/v1",
    tags=["8. Compliance Checks"]
)
app.include_router(
    routes_regulations.router,
    prefix="/api/v1",
    tags=["9. Regulations"]
)
app.include_router(
    routes_incidents.router,
    prefix="/api/v1",
    tags=["10. Incidents"]
)
app.include_router(
    routes_bias.router,
    prefix="/api/v1",
    tags=["11. Bias Audits"]
)
app.include_router(
    routes_seed.router,
    prefix="/api/v1",
    tags=["12. Seed / Data Load"]
)
app.include_router(
    routes_model_cards.router,
    prefix="/api/v1",
    tags=["13. Model Cards"]
)
app.include_router(
    routes_reports.router,
    prefix="/api/v1",
    tags=["13. Reports"]
)
app.include_router(
    routes_monitoring.router,
    prefix="/api/v1",
    tags=["14. Monitoring"]
)
app.include_router(
    routes_dashboard.router,
    prefix="/api/v1",
    tags=["15. Dashboard"]
)
app.include_router(
    routes_auth.router,
    prefix="/api/v1",
    tags=["16. Auth"]
)
app.include_router(
    routes_tasks.router,
    prefix="/api/v1",
    tags=["17. Background Tasks"]
)
app.include_router(
    routes_regulation_mgmt.router,
    prefix="/api/v1",
    tags=["18. Regulation Management (Admin)"]
)
app.include_router(
    routes_notifications.router,
    prefix="/api/v1",
    tags=["19. Notifications"]
)

# --- Root Endpoint / Health Check ---
@app.get("/", tags=["Health Check"])
async def read_root(settings: Settings = Depends(get_settings)):
    """
    Root endpoint for health check.
    Returns the application name and current settings (excluding secrets).
    """
    return {
        "app_name": "Adhi Compliance",
        "log_level": settings.LOG_LEVEL,
        "storage_backend": settings.STORAGE_BACKEND,
        "embedding_model": settings.EMBEDDING_MODEL,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

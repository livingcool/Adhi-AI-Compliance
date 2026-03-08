"""
Alembic environment configuration for Adhi Compliance.

Reads DATABASE_URL from app.config (which reads from .env), imports all SQLAlchemy
models so autogenerate detects the full schema, and supports both offline and online
migration modes.

Usage:
    alembic upgrade head                                   # apply all pending migrations
    alembic downgrade -1                                   # roll back last migration
    alembic revision --autogenerate -m "describe change"   # generate new migration
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Load Alembic ini config ────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import metadata from ALL models ───────────────────────────────────────────
#
# metadata_store.py defines Base, engine, SessionLocal — and at its bottom it
# imports app.store.models, which registers all compliance + AuditLog tables.
# Importing Base from metadata_store is therefore sufficient to capture the
# complete schema.

from app.store.metadata_store import Base  # noqa: E402  (imported after config)
import app.store.models  # noqa: F401  — ensure AuditLog and compliance tables registered

target_metadata = Base.metadata

# ── Pull DATABASE_URL from app config (reads .env automatically) ──────────────

from app.config import settings as _app_settings  # noqa: E402

config.set_main_option("sqlalchemy.url", _app_settings.DATABASE_URL)


# ── Offline migration mode ─────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """
    Offline mode — emits SQL to stdout without requiring a live DB connection.
    Useful for reviewing migrations before applying them.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,  # required for SQLite ALTER TABLE
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Online migration mode ──────────────────────────────────────────────────────

def run_migrations_online() -> None:
    """
    Online mode — connects to the database and applies migrations in a transaction.
    """
    db_url = config.get_main_option("sqlalchemy.url") or ""
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,  # required for SQLite ALTER TABLE
        )

        with context.begin_transaction():
            context.run_migrations()


# ── Dispatch ───────────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

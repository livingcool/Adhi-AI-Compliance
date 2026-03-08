#!/usr/bin/env python3
"""
AWS RDS Migration Script for Adhi AI Compliance
=================================================
Run this script ONCE after provisioning your Amazon RDS instance.
It will:
  1. Test the RDS connection
  2. Run all Alembic migrations against RDS
  3. Load the seed data SQL scripts

Usage:
  python scripts/migrate_to_rds.py

Prerequisites:
  - Set DATABASE_URL in .env to your RDS endpoint BEFORE running
  - Ensure psycopg2-binary and alembic are installed (pip install -r requirements.txt)
  - Ensure your RDS security group allows inbound port 5432 from your IP
"""
import os
import sys
import subprocess
from pathlib import Path

# ── Setup paths ────────────────────────────────────────────
BACKEND_DIR = Path(__file__).parent.parent
SEED_FILES = [
    "supabase_tables_uuid.sql",
    "supabase_seed_data_uuid.sql",
]


def get_db_url() -> str:
    """Read DATABASE_URL from backend/.env or environment."""
    from dotenv import load_dotenv
    # Load backend/.env (script lives in backend/scripts/)
    env_path = BACKEND_DIR / ".env"
    load_dotenv(env_path, override=True)
    url = os.environ.get("DATABASE_URL", "")

    if not url:
        print("❌  DATABASE_URL is not set in backend/.env")
        print(f"    Looked at: {env_path}")
        sys.exit(1)

    if "supabase.co" in url:
        print("⚠️   DATABASE_URL still points to Supabase!")
        print("    Open backend/.env and update DATABASE_URL to your RDS endpoint:")
        print("    DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_RDS_ENDPOINT.ap-south-1.rds.amazonaws.com:5432/adhi_compliance")
        sys.exit(1)

    if "YOUR_RDS" in url or "YOUR_RDS_ENDPOINT" in url:
        print("⚠️   DATABASE_URL still has placeholder values!")
        print("    Replace YOUR_RDS_PASSWORD and YOUR_RDS_ENDPOINT in backend/.env")
        sys.exit(1)

    if "@" not in url:
        print("❌  DATABASE_URL format invalid — expected: postgresql://user:password@host:port/db")
        print(f"    Got: {url}")
        sys.exit(1)

    return url


def test_connection(db_url: str):
    """Verify we can connect to RDS."""
    print("🔍  Testing RDS connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅  Connected to: {version[0][:60]}")
        conn.close()
    except Exception as e:
        print(f"❌  Connection failed: {e}")
        sys.exit(1)


def run_alembic_migrations():
    """Run alembic upgrade head against RDS."""
    print("\n🔄  Running Alembic migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        capture_output=False,
    )
    if result.returncode != 0:
        print("❌  Alembic migration failed.")
        sys.exit(1)
    print("✅  Alembic migrations complete.")


def enable_pgvector(db_url: str):
    """Enable the pgvector extension on RDS."""
    print("\n🔌  Enabling pgvector extension...")
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅  pgvector extension enabled.")
        conn.close()
    except Exception as e:
        print(f"⚠️   pgvector extension: {e} (may already exist)")


def load_seed_data(db_url: str):
    """Load seed SQL files into RDS."""
    print("\n🌱  Loading seed data...")
    for sql_file in SEED_FILES:
        fpath = BACKEND_DIR / sql_file
        if not fpath.exists():
            print(f"   ⚠️  Seed file not found: {sql_file} — skipping")
            continue
        print(f"   📄  Loading {sql_file}...")
        result = subprocess.run(
            ["psql", db_url, "-f", str(fpath)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"   ⚠️  {sql_file} errors:\n{result.stderr[:500]}")
        else:
            print(f"   ✅  {sql_file} loaded successfully.")


if __name__ == "__main__":
    print("=" * 60)
    print("  Adhi AI Compliance — AWS RDS Migration")
    print("=" * 60)

    db_url = get_db_url()
    # Show host:port/db only — hide password
    host_part = db_url.split('@')[-1]
    print(f"\n🎯  Target RDS: {host_part}")

    test_connection(db_url)
    enable_pgvector(db_url)
    run_alembic_migrations()
    load_seed_data(db_url)

    print("\n" + "=" * 60)
    print("✅  Migration to Amazon RDS complete!")
    print("    Next: Update REDIS_URL to ElastiCache endpoint")
    print("          Set AWS_S3_BUCKET and upload test file")
    print("          Test Bedrock API: LLM_PROVIDER=bedrock")
    print("=" * 60)

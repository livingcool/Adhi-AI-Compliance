#!/usr/bin/env python3
"""
Test database connection and FastAPI app
"""
from app.config import settings
print('Database URL:', settings.DATABASE_URL[:50] + '...')

# Test FastAPI app import
from app.main import app
print('SUCCESS: FastAPI app imported successfully')

# Test connection
from app.store.models import get_db_session
from sqlalchemy import text
db = next(get_db_session())
print('SUCCESS: Database connection established!')

# Count tables (SQLite-compatible)
query = "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
result = db.execute(text(query))
table_count = result.scalar()
print(f'SUCCESS: Found {table_count} tables in database')

# List table names
query2 = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
result2 = db.execute(text(query2))
tables = [row[0] for row in result2.fetchall()]
print(f'Tables: {", ".join(tables)}')

db.close()
print('Database test complete!')
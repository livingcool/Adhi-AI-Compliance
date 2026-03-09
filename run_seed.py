import os
import sys

sys.path.insert(0, os.path.abspath('backend'))
from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy import text
from app.store.models import SessionLocal

def seed_db():
    print("Connecting to RDS...")
    db = SessionLocal()
    print("Connected.")
    
    sql_path = 'ADHI-SQL-SCRATCH/10_insert_sample_data.sql'
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Split the SQL script by semicolons to execute statements individually 
    # (since SQLAlchemy's db.execute doesn't always handle full raw scripts well if they contain multiple queries)
    
    # Actually, SQLAlchemy with psycopg2 handles multiple statements if wrapped in text(), 
    # but let's be safe.
    
    try:
        db.execute(text(sql))
        db.commit()
        print("✅ Sample data successfully inserted into RDS.")
    except Exception as e:
        print("Exception:", str(e))
        db.rollback()

if __name__ == "__main__":
    seed_db()

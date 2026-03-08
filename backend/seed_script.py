import os
import sqlalchemy
from sqlalchemy import create_engine

db_url = "postgresql://postgres:G22a05n%4003@adhi-compliance-db.chq0mqkqaozv.ap-south-2.rds.amazonaws.com:5432/postgres"
engine = create_engine(db_url)

sql_file = r"e:\RootedAI\SAAS\Adhi-AI-Compliance\ADHI-SQL-SCRATCH\10_insert_sample_data.sql"
with open(sql_file, 'r', encoding='utf-8') as f:
    sql = f.read()

with engine.connect() as conn:
    raw_conn = conn.connection
    cursor = raw_conn.cursor()
    cursor.execute(sql)
    raw_conn.commit()

print("Successfully executed SQL script.")

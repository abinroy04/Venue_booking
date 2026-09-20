"""
Database Initializer & Migration Script for Neon PostgreSQL
Runs schema.sql, functions.sql, triggers.sql, and sample_data.sql on Neon database.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')


def run_sql_file(conn, file_path):
    """Read and execute a .sql script file"""
    if not os.path.exists(file_path):
        print(f"[WARNING] SQL file not found: {file_path}")
        return
        
    print(f"[INFO] Executing {os.path.basename(file_path)}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
        
    with conn.cursor() as cur:
        cur.execute(sql_content)
    conn.commit()
    print(f"[SUCCESS] Executed {os.path.basename(file_path)} successfully.")


def initialize_database():
    if not DB_URL:
        print("[ERROR] DATABASE_URL is not set in your .env file.")
        print("[TIP] Please add your Neon connection string to .env file first!")
        sys.exit(1)
        
    print("[INFO] Connecting to Neon PostgreSQL...")
    try:
        conn = psycopg2.connect(DB_URL)
        print("[SUCCESS] Connection successful!")
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_dir = os.path.join(base_dir, 'database')
        
        schema_path = os.path.join(db_dir, 'schema.sql')
        sample_path = os.path.join(db_dir, 'sample_data.sql')
        
        run_sql_file(conn, schema_path)
        run_sql_file(conn, sample_path)
        
        conn.close()
        print("\n[SUCCESS] Database initialization complete!")
    except Exception as e:
        print(f"[ERROR] Database Initialization Failed: {e}")


if __name__ == '__main__':
    initialize_database()

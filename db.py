"""
Database Helper Module for Neon PostgreSQL
Provides PostgreSQL connection pooling and Dict cursor querying
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Create and return a new database connection"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing in .env file")
    
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn


def execute_query(sql, params=None, fetch=None):
    """
    Execute a SQL query safely.
    
    Args:
        sql (str): SQL query string
        params (tuple/dict): Query parameters
        fetch (str): 'one', 'all', or None
        
    Returns:
        dict / list of dicts / None
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            
            if fetch == 'one':
                result = cur.fetchone()
                if result:
                    result = dict(result)
            elif fetch == 'all':
                result = [dict(r) for r in cur.fetchall()]
            else:
                result = None
                
            conn.commit()
            return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def fetch_one(sql, params=None):
    """Helper to fetch a single record as a dict"""
    return execute_query(sql, params, fetch='one')


def fetch_all(sql, params=None):
    """Helper to fetch all records as a list of dicts"""
    return execute_query(sql, params, fetch='all')

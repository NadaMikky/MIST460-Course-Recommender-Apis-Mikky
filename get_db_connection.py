import pyodbc
import os
from fastapi import HTTPException
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def _rows_to_dicts(cursor):
    """Convert query results to list of dictionaries"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Dependency to get DB connection
def get_db_connection():
    # Get environment
    env = os.getenv('ENVIRONMENT', 'PRODUCTION').upper()

    if env == 'PRODUCTION':
        DB_SERVER = os.getenv('DB_SERVER')
        DB_DATABASE = os.getenv('DB_DATABASE')
        DB_USERNAME = os.getenv('DB_USERNAME')
        DB_PASSWORD = os.getenv('DB_PASSWORD')

        connection_string = (
            'DRIVER={ODBC Driver 18 for SQL Server};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_DATABASE};'
            f'UID={DB_USERNAME};'
            f'PWD={DB_PASSWORD};'
            'TrustServerCertificate=no;'
            'Connection Timeout=30;'
            'Encrypt=yes;'
        )
    else:        
        DB_SERVER = "localhost"
        DB_DATABASE = "Homework3Group1;"

        connection_string = (
            'DRIVER={ODBC Driver 18 for SQL Server};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_DATABASE};'
            'TrustServerCertificate=yes;'
            'Trusted_Connection=yes;'
            'Connection Timeout=30;'
            'Encrypt=yes;'
        )        

    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
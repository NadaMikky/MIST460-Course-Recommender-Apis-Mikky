from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from get_db_connection import get_db_connection, _rows_to_dicts
import pyodbc

router = APIRouter()

# 1. validate_user
# @router.post("/validate_user")
def validate_user(
    username: str,
    password: str
):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the stored procedure
    cursor.execute("{call procValidateUser(?, ?)}", (username, password) )

    # Fetch results
    row = cursor. fetchone ()
    cursor. close()
    conn.close()

    # Convert to list of dicts
    results = [
    {"AppUserID": row.AppUserID, "FullName": row. FullName}
    ]
    return {"data": results}

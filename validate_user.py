from get_db_connection import get_db_connection

def validate_user(
    username: str,
    password: str
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the stored procedure
    cursor.execute("{call procValidateUser(?, ?)}", (username, password))

    # Fetch results
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    # Convert to list of dicts
    results = [
        {"AppUserID": row.AppUserID, "FullName": row.FullName}
    ]
    return {"data": results}
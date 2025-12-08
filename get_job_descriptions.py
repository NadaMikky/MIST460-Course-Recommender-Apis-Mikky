from get_db_connection import get_db_connection

def get_job_descriptions():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the stored procedure
    cursor.execute("{call procGetAllJobDescriptions}")

    # Fetch results
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to list of dicts
    results = [
        {"JobDescription": row.JobDescription, "DetailedJobDescription": row.DetailedJobDescription}
        for row in rows
    ]
    return {"data": results}

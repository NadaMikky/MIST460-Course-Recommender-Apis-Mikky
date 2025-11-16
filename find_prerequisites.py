from get_db_connection import get_db_connection

def find_prerequisites(
    subjectCode: str,
    courseNumber: str
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the stored procedure
    cursor.execute("{call procFindPrerequisites(?, ?)}", (subjectCode, courseNumber))

    # Fetch results
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to list of dicts
    results = [
        {"SubjectCode": row.SubjectCode, "CourseNumber": row.CourseNumber}
        for row in rows
    ]
    return {"data": results}
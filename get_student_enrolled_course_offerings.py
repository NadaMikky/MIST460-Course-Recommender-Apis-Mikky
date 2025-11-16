from get_db_connection import get_db_connection

def get_student_enrolled_course_offerings(
    studentID: int
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the stored procedure
    cursor.execute("{call procGetStudentEnrolledCourseOfferings(?)}", studentID)

    # Fetch results
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to list of dicts
    results = [
        {"CourseOfferingID": row.CourseOfferingID, "CRN": row.CRN, "SubjectCode": row.SubjectCode, "CourseNumber": row.CourseNumber, 
        "EnrollmentStatus": row.EnrollmentStatus, "LastUpdate": row.LastUpdate}
        for row in rows
    ]
    return {"data": results}
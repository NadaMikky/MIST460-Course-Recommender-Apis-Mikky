from get_db_connection import get_db_connection

def drop_student_from_course_offering(
    studentID: int,
    courseOfferingID: int
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the stored procedure
    cursor.execute("{call procDropStudentFromCourseOfferingCalled(?, ?)}", (studentID, courseOfferingID))    
    row = cursor.fetchone()
    
    cursor.close()
    conn.commit()
    conn.close()
    
    results = [
        {"EnrollmentStatus": row.EnrollmentStatus, "LastUpdate": row.LastUpdate}
    ]

    return {
        "data": results
    }
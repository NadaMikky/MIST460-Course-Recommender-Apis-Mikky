from get_db_connection import get_db_connection

def enroll_student_in_course_offering(
    studentID: int, 
    courseOfferingID: int
):
    
    conn = get_db_connection()    
    cursor = conn.cursor()
    
    cursor.execute("{call procEnrollStudentInCourseOfferingCalled(?, ?)}", (studentID, courseOfferingID))
    
    row = cursor.fetchone()

    cursor.close()
    conn.commit()
    conn.close()
    
    results = [
        {"EnrollmentResponse": row.EnrollmentResponse, "EnrollmentSucceeded": row.EnrollmentSucceeded}
    ]

    return {
        "data": results
    }
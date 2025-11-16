import os
import pyodbc
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

# ==========================================================
#                Import Functionality Modules
# ==========================================================
from validate_user import validate_user
from check_prereqs import check_prereqs
from find_current_semester_course_offering import find_current_semester_course_offering
from find_prerequisites import find_prerequisites
from get_student_enrolled_course_offerings import get_student_enrolled_course_offerings
from enroll_student import enroll_student
from drop_student import drop_student

app = FastAPI(title="Course Recommender APIs")

# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    env = "PRODUCTION"

    if env == "PRODUCTION":
        DB_SERVER = os.getenv("DB_SERVER")  # tcp:mist-mikky.database.windows.net,1433
        DB_DATABASE = os.getenv("DB_DATABASE")  # Course_Recommender_MikkyDB
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")

        if DB_SERVER.startswith("tcp:"):
            DB_SERVER = DB_SERVER[4:]

        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
    else:
        DB_SERVER = "localhost"
        DB_DATABASE = "Course_Recommender_MikkyDB"
        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
            "Encrypt=yes;"
            "Connection Timeout=30;"
        )

    try:
        return pyodbc.connect(connection_string)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# -----------------------------
# Utility
# -----------------------------
def _rows_to_dicts(cursor, rows):
    cols = [c[0] for c in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in rows]

# ==========================================================
#                Define API Endpoints
# ==========================================================

@app.get("/validate_user/")
def validate_user_api(username: str, password: str):
    return validate_user(username, password)


@app.get("/check_prereqs/")
def check_prereqs_api(studentID: int, subjectCode: str, courseNumber: str):
    return check_prereqs(student_id, subject_code, course_number)


@app.get("/find_current_semester_course_offerings/")
def find_current_semester_course_offerings_api(subject_code: str, course_number: str):
    return find_current_semester_course_offerings(subject_code, course_number)


@app.get("/find_prerequisites/")
def find_prerequisites_api(subject_code: str, CourseNumber: str):
    return find_prerequisites(subject_code, CourseNumber)


@app.get("/get_student_enrolled_course_offerings/")
def get_student_enrolled_course_offerings_api(studentID: str):
    return get_student_enrolled_course_offerings(studentID)


@app.post("/enroll_student/")
def enroll_student_api( studentID: int, courseOfferingID: int):
    return enroll_student(studentID, courseOfferingID)


@app.post("/drop_student/")
def drop_student_api(studentID: str, courseOfferingID: int):
    return drop_student(studentID, courseOfferingID)

@app.get("/")
def read_root():
    return {"message": "Course Recommender API is running"}

def main():
    """Main entry point for the API server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
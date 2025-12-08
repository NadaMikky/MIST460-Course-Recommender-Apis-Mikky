import os
import get_job_descriptions
import get_recommendation_for_job_description
import pyodbc
from fastapi import FastAPI, HTTPException, Query
from pathlib import Path

app = FastAPI(title="Course Recommender APIs")

# Minimal DB helper kept (won't connect on import)
def get_db_connection():
    env = os.getenv("ENVIRONMENT", "PRODUCTION").upper()
    DB_SERVER = os.getenv("DB_SERVER") or ""
    DB_DATABASE = os.getenv("DB_DATABASE") or ""
    DB_USERNAME = os.getenv("DB_USERNAME") or ""
    DB_PASSWORD = os.getenv("DB_PASSWORD") or ""

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
    try:
        return pyodbc.connect(connection_string)
    except Exception as e:
        # don't raise on import; callers can handle connection errors
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# Lightweight health endpoints (do not touch DB)
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    # simple readiness check that avoids DB connection at module import
    return {"ready": True}


# ==========================================================
# Define endpoints that import DB-using modules lazily.
# This prevents import-time failures (Azure deploy often imports the module)
# ==========================================================

@app.get("/validate_user/")
def validate_user_api(username: str, password: str):
    # import inside handler to avoid DB code at module import time
    from validate_user import validate_user
    return validate_user(username, password)


@app.get("/check_if_student_has_taken_all_prerequisites_for_course/")
def check_prereqs_api(studentID: int, subjectCode: str, courseNumber: str):
    from check_prereqs import check_if_student_has_taken_all_prerequisites_for_course
    return check_if_student_has_taken_all_prerequisites_for_course(studentID, subjectCode, courseNumber)


@app.get("/find_current_semester_course_offerings/")
def find_current_semester_course_offerings_api(subjectCode: str, courseNumber: str):
    from find_current_semester_course_offering import find_current_semester_course_offerings
    return find_current_semester_course_offerings(subjectCode, courseNumber)


@app.get("/find_prerequisites/")
def find_prerequisites_api(subjectCode: str, courseNumber: str):
    from find_prerequisites import find_prerequisites
    return find_prerequisites(subjectCode, courseNumber)


@app.get("/get_student_enrolled_course_offerings/")
def get_student_enrolled_course_offerings_api(studentID: int):
    from get_student_enrolled_course_offerings import get_student_enrolled_course_offerings
    return get_student_enrolled_course_offerings(studentID)


@app.post("/enroll_student_in_course_offering/")
def enroll_student_api(studentID: int, courseOfferingID: int):
    from enroll_student import enroll_student_in_course_offering
    return enroll_student_in_course_offering(studentID, courseOfferingID)


@app.post("/drop_student_from_course_offering/")
def drop_student_api(studentID: int, courseOfferingID: int):
    from drop_student import drop_student_from_course_offering
    return drop_student_from_course_offering(studentID, courseOfferingID)

@app.get("/get_job_descriptions/")
def get_job_descriptions_api():
    return get_job_descriptions()

@app.get("/get_recommendation_for_job_description")
async def get_recommendations_endpoint(
    jobDescription: str = Query(..., description="The job description text"),
    studentID: int = Query(..., description="The student ID")
    ):
    return get_recommendation_for_job_description(jobDescription, studentID)

@app.get("/")
def read_root():
    return {"message": "Course Recommender API is running"}


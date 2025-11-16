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
from check_prereqs import check_if_student_has_taken_all_prerequisites_for_course
from find_current_semester_course_offering import find_current_semester_course_offerings
from find_prerequisites import find_prerequisites
from get_student_enrolled_course_offerings import get_student_enrolled_course_offerings
from enroll_student import enroll_student_in_course_offering
from drop_student import drop_student_from_course_offering

app = FastAPI(title="Course Recommender APIs")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/check_if_student_has_taken_all_prerequisites_for_course/")
def check_prereqs_api(studentID: int, subjectCode: str, courseNumber: str):
    return check_if_student_has_taken_all_prerequisites_for_course(studentID, subjectCode, courseNumber)


@app.get("/find_current_semester_course_offerings/")
def find_current_semester_course_offerings_api(subjectCode: str, courseNumber: str):
    return find_current_semester_course_offerings(subjectCode, courseNumber)


@app.get("/find_prerequisites/")
def find_prerequisites_api(subjectCode: str, courseNumber: str):
    return find_prerequisites(subjectCode, courseNumber)


@app.get("/get_student_enrolled_course_offerings/")
def get_student_enrolled_course_offerings_api(studentID: int):
    return get_student_enrolled_course_offerings(studentID)


@app.post("/enroll_student_in_course_offering/")
def enroll_student_api(studentID: int, courseOfferingID: int):
    return enroll_student_in_course_offering(studentID, courseOfferingID)


@app.post("/drop_student_from_course_offering/")
def drop_student_api(studentID: int, courseOfferingID: int):
    return drop_student_from_course_offering(studentID, courseOfferingID)


@app.get("/")
def read_root():
    return {"message": "Course Recommender API is running"}

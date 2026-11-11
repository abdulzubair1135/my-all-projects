from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import json
from datetime import datetime
import re

app = FastAPI(title="School Management System")

# Data models
class Student(BaseModel):
    id: Optional[int] = None
    name: str
    grade: str
    section: str
    email: str
    phone: str
    address: str
    date_of_birth: str

class AttendanceRecord(BaseModel):
    id: Optional[int] = None
    student_id: int
    student_name: str
    date: str
    status: str  # Present, Absent, Late
    check_in: Optional[str] = None
    check_out: Optional[str] = None

class AcademicRecord(BaseModel):
    id: Optional[int] = None
    student_id: int
    subject: str
    grade: float
    term: str
    year: str

# In-memory storage
students_db: Dict[int, Student] = {}
attendance_db: Dict[int, AttendanceRecord] = {}
academic_db: Dict[int, AcademicRecord] = {}
student_id_counter = 1
attendance_id_counter = 1
academic_id_counter = 1

# Initialize with sample data
def init_sample_data():
    global student_id_counter, attendance_id_counter, academic_id_counter
    
    # Sample Students
    sample_students = [
        Student(name="John Doe", grade="12", section="A", email="john.doe@school.com", 
                phone="555-0101", address="123 Main St", date_of_birth="2006-05-15"),
        Student(name="Jane Smith", grade="11", section="B", email="jane.smith@school.com",
                phone="555-0102", address="456 Oak Ave", date_of_birth="2007-08-22"),
        Student(name="Mike Johnson", grade="12", section="A", email="mike.j@school.com",
                phone="555-0103", address="789 Pine Rd", date_of_birth="2006-11-30"),
        Student(name="Emily Davis", grade="10", section="C", email="emily.d@school.com",
                phone="555-0104", address="321 Elm St", date_of_birth="2008-03-10"),
        Student(name="Chris Wilson", grade="9", section="B", email="chris.w@school.com",
                phone="555-0105", address="654 Maple Dr", date_of_birth="2009-07-19"),
    ]
    
    for student in sample_students:
        student.id = student_id_counter
        students_db[student_id_counter] = student
        student_id_counter += 1
    
    # Sample Attendance
    today = datetime.now().strftime("%Y-%m-%d")
    sample_attendance = [
        AttendanceRecord(student_id=1, student_name="John Doe", date=today, status="Present", 
                        check_in="08:15", check_out="15:30"),
        AttendanceRecord(student_id=2, student_name="Jane Smith", date=today, status="Present",
                        check_in="08:20", check_out="15:25"),
        AttendanceRecord(student_id=3, student_name="
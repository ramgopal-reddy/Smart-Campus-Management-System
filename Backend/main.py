from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pydantic import BaseModel
import os
import uuid
from datetime import datetime

from database import SessionLocal, engine
from models import (
    Base,
    Student,
    Attendance,
    FoodOrder,
    Block,
    Classroom,
    Course,
    Faculty,
    FacultyCourse,
    MakeupClass,
    MakeupAttendance
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart LPU Campus Management System")

# -------------------------
# CORS CONFIG
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://smart-campus-management-system-lcgz.onrender.com"
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# DATABASE DEPENDENCY
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# PYDANTIC SCHEMAS
# -------------------------
class StudentCreate(BaseModel):
    student_name: str
    roll_number: str
    student_email: str

class AttendanceCreate(BaseModel):
    roll_number: str
    status: str
    student_email: str

class FoodOrderCreate(BaseModel):
    student_name: str
    food_item: str
    break_time: str
    student_email: str

class BlockCreate(BaseModel):
    name: str

class ClassroomCreate(BaseModel):
    room_number: str
    capacity: int
    block_id: int

class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    weekly_hours: int

class FacultyCreate(BaseModel):
    name: str
    email: str

class FacultyCourseAssign(BaseModel):
    faculty_id: int
    course_id: int
    assigned_hours: int

# ---- Makeup Class Schemas ----
class MakeupClassCreate(BaseModel):
    faculty_id: int
    course_id: int
    scheduled_time: str

class MarkRemedialAttendance(BaseModel):
    roll_number: str
    remedial_code: str

# -------------------------
# EMAIL FUNCTION
# -------------------------
def send_email(to_email: str, subject: str, message_text: str):
    try:
        message = Mail(
            from_email=os.getenv("DEVELOPER_EMAIL"),
            to_emails=to_email,
            subject=subject,
            plain_text_content=message_text
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        print("Email error:", e)

# ==========================================================
# STUDENT MANAGEMENT
# ==========================================================
@app.post("/add_student")
def add_student(data: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.roll == data.roll_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already exists")

    student = Student(
        name=data.student_name,
        roll=data.roll_number,
        email=data.student_email
    )
    db.add(student)
    db.commit()
    return {"message": "Student added successfully"}

@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [{"roll": s.roll, "name": s.name, "email": s.email} for s in students]

# ==========================================================
# REGULAR ATTENDANCE
# ==========================================================
@app.post("/mark_attendance")
def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.roll == data.roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    record = Attendance(roll=data.roll_number, status=data.status)
    db.add(record)
    db.commit()

    message = (
        "You were marked ABSENT today."
        if data.status.lower() == "absent"
        else "You were marked PRESENT today."
    )

    send_email(data.student_email, "Attendance Update", message)

    return {"message": "Attendance marked successfully"}

@app.get("/attendance_history")
def attendance_history(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    return [{"roll": r.roll, "status": r.status} for r in records]

# ==========================================================
# MAKE-UP CLASS MODULE
# ==========================================================

# ---- Schedule Makeup Class ----
@app.post("/schedule_makeup_class")
def schedule_makeup_class(data: MakeupClassCreate, db: Session = Depends(get_db)):

    faculty = db.query(Faculty).filter(Faculty.id == data.faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    remedial_code = str(uuid.uuid4())[:8].upper()

    makeup = MakeupClass(
        faculty_id=data.faculty_id,
        course_id=data.course_id,
        scheduled_time=data.scheduled_time,
        remedial_code=remedial_code,
        created_at=datetime.utcnow()
    )

    db.add(makeup)
    db.commit()
    db.refresh(makeup)

    return {
        "message": "Make-up class scheduled successfully",
        "remedial_code": remedial_code
    }

# ---- Mark Makeup Attendance ----
@app.post("/mark_makeup_attendance")
def mark_makeup_attendance(data: MarkRemedialAttendance, db: Session = Depends(get_db)):

    student = db.query(Student).filter(Student.roll == data.roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    makeup = db.query(MakeupClass).filter(
        MakeupClass.remedial_code == data.remedial_code
    ).first()

    if not makeup:
        raise HTTPException(status_code=404, detail="Invalid remedial code")

    existing = db.query(MakeupAttendance).filter(
        MakeupAttendance.makeup_class_id == makeup.id,
        MakeupAttendance.roll == data.roll_number
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked")

    attendance = MakeupAttendance(
        makeup_class_id=makeup.id,
        roll=data.roll_number,
        status="Present"
    )

    db.add(attendance)
    db.commit()

    return {"message": "Make-up attendance marked successfully"}

@app.get("/makeup_attendance_history")
def makeup_attendance_history(db: Session = Depends(get_db)):
    records = db.query(MakeupAttendance).all()
    return [
        {
            "makeup_class_id": r.makeup_class_id,
            "roll": r.roll,
            "status": r.status
        }
        for r in records
    ]

# ==========================================================
# ROOT
# ==========================================================
@app.get("/")
def root():
    return {"message": "Smart LPU Campus Management System API Running Successfully"}

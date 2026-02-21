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
# CORS CONFIG (FIXED)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # safe for now (can restrict later)
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

# ==========================================================
# PYDANTIC SCHEMAS
# ==========================================================
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

# Make-up schemas
class MakeupClassCreate(BaseModel):
    faculty_id: int
    course_id: int
    scheduled_time: str

class MarkRemedialAttendance(BaseModel):
    roll_number: str
    remedial_code: str

# ==========================================================
# EMAIL FUNCTION
# ==========================================================
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

@app.get("/student/{roll_number}")
def get_student(roll_number: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.roll == roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"name": student.name, "roll": student.roll, "email": student.email}

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

    send_email(
        data.student_email,
        "Attendance Update",
        f"You were marked {data.status.upper()} today."
    )

    return {"message": "Attendance marked successfully"}

@app.get("/attendance_history")
def attendance_history(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    return [{"roll": r.roll, "status": r.status} for r in records]

# ==========================================================
# FOOD MODULE
# ==========================================================
@app.post("/order_food")
def order_food(data: FoodOrderCreate, db: Session = Depends(get_db)):
    order = FoodOrder(
        student=data.student_name,
        food=data.food_item,
        time=data.break_time
    )
    db.add(order)
    db.commit()

    send_email(
        data.student_email,
        "Food Order Confirmation",
        f"Your order for {data.food_item} at {data.break_time} is confirmed."
    )

    return {"message": "Food order placed successfully"}

@app.get("/food_order_history")
def food_order_history(db: Session = Depends(get_db)):
    orders = db.query(FoodOrder).all()
    return [{"student": o.student, "food": o.food, "time": o.time} for o in orders]

# ==========================================================
# BLOCKS & CLASSROOM
# ==========================================================
@app.post("/add_block")
def add_block(data: BlockCreate, db: Session = Depends(get_db)):
    block = Block(name=data.name)
    db.add(block)
    db.commit()
    return {"message": "Block added successfully"}

@app.get("/blocks")
def get_blocks(db: Session = Depends(get_db)):
    return db.query(Block).all()

@app.post("/add_classroom")
def add_classroom(data: ClassroomCreate, db: Session = Depends(get_db)):
    classroom = Classroom(
        room_number=data.room_number,
        capacity=data.capacity,
        block_id=data.block_id
    )
    db.add(classroom)
    db.commit()
    return {"message": "Classroom added successfully"}

@app.get("/classrooms")
def get_classrooms(db: Session = Depends(get_db)):
    return db.query(Classroom).all()

# ==========================================================
# COURSES & FACULTY
# ==========================================================
@app.post("/add_course")
def add_course(data: CourseCreate, db: Session = Depends(get_db)):
    course = Course(
        course_code=data.course_code,
        course_name=data.course_name,
        weekly_hours=data.weekly_hours
    )
    db.add(course)
    db.commit()
    return {"message": "Course added successfully"}

@app.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@app.post("/add_faculty")
def add_faculty(data: FacultyCreate, db: Session = Depends(get_db)):
    faculty = Faculty(name=data.name, email=data.email)
    db.add(faculty)
    db.commit()
    return {"message": "Faculty added successfully"}

@app.get("/faculty")
def get_faculty(db: Session = Depends(get_db)):
    return db.query(Faculty).all()

@app.post("/assign_course")
def assign_course(data: FacultyCourseAssign, db: Session = Depends(get_db)):
    assignment = FacultyCourse(
        faculty_id=data.faculty_id,
        course_id=data.course_id,
        assigned_hours=data.assigned_hours
    )
    db.add(assignment)
    db.commit()
    return {"message": "Course assigned successfully"}

# ==========================================================
# UTILIZATION
# ==========================================================
@app.get("/faculty_workload/{faculty_id}")
def faculty_workload(faculty_id: int, db: Session = Depends(get_db)):
    assignments = db.query(FacultyCourse).filter(
        FacultyCourse.faculty_id == faculty_id
    ).all()

    total_hours = sum(a.assigned_hours for a in assignments)
    STANDARD_HOURS = 20
    utilization = (total_hours / STANDARD_HOURS) * 100

    return {
        "total_assigned_hours": total_hours,
        "utilization_percentage": round(utilization, 2)
    }

# ==========================================================
# MAKE-UP CLASS MODULE
# ==========================================================
@app.post("/schedule_makeup_class")
def schedule_makeup_class(data: MakeupClassCreate, db: Session = Depends(get_db)):

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
        "message": "Make-up class scheduled",
        "remedial_code": remedial_code
    }

@app.post("/mark_makeup_attendance")
def mark_makeup_attendance(data: MarkRemedialAttendance, db: Session = Depends(get_db)):

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
        raise HTTPException(status_code=400, detail="Already marked")

    attendance = MakeupAttendance(
        makeup_class_id=makeup.id,
        roll=data.roll_number,
        status="Present"
    )

    db.add(attendance)
    db.commit()

    return {"message": "Make-up attendance marked"}

@app.get("/makeup_attendance_history")
def makeup_attendance_history(db: Session = Depends(get_db)):
    records = db.query(MakeupAttendance).all()

    return [
        {
            "id": r.id,
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

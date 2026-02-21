from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pydantic import BaseModel
import os

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
    FacultyCourse
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart LPU Campus Management System")


# -------------------------
# CORS CONFIG (REMOVE "*" IN PRODUCTION)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://your-frontend-domain.onrender.com"
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

# -------------------------
# SEND EMAIL FUNCTION
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


# -------------------------
# ADD STUDENT
# -------------------------
@app.post("/add_student")
def add_student(data: StudentCreate, db: Session = Depends(get_db)):

    existing_student = db.query(Student).filter(Student.roll == data.roll_number).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student with this roll number already exists")

    student = Student(
        name=data.student_name,
        roll=data.roll_number,
        email=data.student_email
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return {"message": "Student added successfully"}


# -------------------------
# MARK ATTENDANCE
# -------------------------
@app.post("/mark_attendance")
def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):

    student = db.query(Student).filter(Student.roll == data.roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    record = Attendance(
        roll=data.roll_number,
        status=data.status
    )

    db.add(record)
    db.commit()

    subject = "Attendance Alert"

    if data.status.lower() == "absent":
        message = "You were marked ABSENT today. Please contact faculty."
    else:
        message = "You were marked PRESENT today. Happy Learning."

    send_email(data.student_email, subject, message)

    return {"message": "Attendance marked successfully"}


# -------------------------
# ATTENDANCE HISTORY
# -------------------------
@app.get("/attendance_history")
def attendance_history(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()

    return [
        {"roll": r.roll, "status": r.status}
        for r in records
    ]


# -------------------------
# ORDER FOOD
# -------------------------
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


# -------------------------
# FOOD ORDER HISTORY
# -------------------------
@app.get("/food_order_history")
def food_order_history(db: Session = Depends(get_db)):

    orders = db.query(FoodOrder).all()

    return [
        {"student": o.student, "food": o.food, "time": o.time}
        for o in orders
    ]


# -------------------------
# GET STUDENT BY ROLL
# -------------------------
@app.get("/student/{roll_number}")
def get_student(roll_number: str, db: Session = Depends(get_db)):

    student = db.query(Student).filter(Student.roll == roll_number).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "name": student.name,
        "roll": student.roll,
        "email": student.email
    }

@app.get("/students")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [{"roll": s.roll, "name": s.name, "email": s.email} for s in students]



# Add block
@app.post("/add_block")
def add_block(data: BlockCreate, db: Session = Depends(get_db)):
    block = Block(name=data.name)
    db.add(block)
    db.commit()
    return {"message": "Block added successfully"}

# Blocks
@app.get("/blocks")
def get_blocks(db: Session = Depends(get_db)):
    blocks = db.query(Block).all()
    return [{"id": b.id, "name": b.name} for b in blocks]

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

# Classrooms
@app.get("/classrooms")
def get_classrooms(db: Session = Depends(get_db)):
    classrooms = db.query(Classroom).all()
    return [
        {
            "id": c.id,
            "room_number": c.room_number,
            "capacity": c.capacity,
            "block_id": c.block_id
        }
        for c in classrooms
    ]

# Courses

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
    courses = db.query(Course).all()
    return [
        {
            "id": c.id,
            "code": c.course_code,
            "name": c.course_name,
            "weekly_hours": c.weekly_hours
        }
        for c in courses
    ]

# Faculty
@app.post("/add_faculty")
def add_faculty(data: FacultyCreate, db: Session = Depends(get_db)):
    faculty = Faculty(name=data.name, email=data.email)
    db.add(faculty)
    db.commit()
    return {"message": "Faculty added successfully"}


@app.get("/faculty")
def get_faculty(db: Session = Depends(get_db)):
    faculty = db.query(Faculty).all()
    return [
        {"id": f.id, "name": f.name, "email": f.email}
        for f in faculty
    ]

# Assign Course to faculty
@app.post("/assign_course")
def assign_course(data: FacultyCourseAssign, db: Session = Depends(get_db)):
    assignment = FacultyCourse(
        faculty_id=data.faculty_id,
        course_id=data.course_id,
        assigned_hours=data.assigned_hours
    )
    db.add(assignment)
    db.commit()
    return {"message": "Course assigned to faculty successfully"}


# Classrooms Utilization

@app.get("/classroom_utilization/{classroom_id}")
def classroom_utilization(classroom_id: int, db: Session = Depends(get_db)):

    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    student_count = db.query(Student).count()  # Simplified for now

    utilization = (student_count / classroom.capacity) * 100 if classroom.capacity else 0

    return {"utilization_percentage": round(utilization, 2)}

# Block Utilization
@app.get("/block_utilization/{block_id}")
def block_utilization(block_id: int, db: Session = Depends(get_db)):

    classrooms = db.query(Classroom).filter(Classroom.block_id == block_id).all()

    total_capacity = sum(c.capacity for c in classrooms)

    student_count = db.query(Student).count()

    utilization = (student_count / total_capacity) * 100 if total_capacity else 0

    return {"utilization_percentage": round(utilization, 2)}

# Faculty workload

@app.get("/faculty_workload/{faculty_id}")
def faculty_workload(faculty_id: int, db: Session = Depends(get_db)):

    assignments = db.query(FacultyCourse).filter(FacultyCourse.faculty_id == faculty_id).all()

    total_hours = sum(a.assigned_hours for a in assignments)

    STANDARD_HOURS = 20

    utilization = (total_hours / STANDARD_HOURS) * 100

    return {
        "total_assigned_hours": total_hours,
        "utilization_percentage": round(utilization, 2)
    }

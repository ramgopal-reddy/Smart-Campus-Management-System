from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pydantic import BaseModel
import os

from database import SessionLocal, engine
from models import Base, Student, Attendance, FoodOrder

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

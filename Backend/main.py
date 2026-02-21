from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

from database import SessionLocal, engine
from models import Base, Student, Attendance, FoodOrder

# Create tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart LPU Campus Management System")

# Add CORS middleware BEFORE defining your routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",      # Django development server
        "http://localhost:8000",         # Django development server (alternative)
        "https://127.0.0.1:8000",     # HTTPS Django server
        "https://localhost:8000",        # HTTPS Django server (alternative)
        "https://your-render-domain.onrender.com",  # Your production frontend
        "*"  # For development only - remove in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
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
# SEND EMAIL FUNCTION
# -------------------------
def send_email(to_email, subject, message_text):
    message = Mail(
        from_email=os.getenv("DEVELOPER_EMAIL"),
        to_emails=to_email,
        subject=subject,
        plain_text_content=message_text
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        print("Email error:", e)


# -------------------------
# ADD STUDENT
# -------------------------
@app.post("/add_student")
def add_student(student_name: str, roll_number: str, student_email: str, db: Session = Depends(get_db)):
    student = Student(
        name=student_name,
        roll=roll_number,
        email=student_email
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return {"message": "Student added successfully"}


# -------------------------
# MARK ATTENDANCE
# -------------------------
@app.post("/mark_attendance")
def mark_attendance(roll_number: str, status: str, student_email: str, db: Session = Depends(get_db)):
    record = Attendance(
        roll=roll_number,
        status=status
    )

    db.add(record)
    db.commit()

    subject = "Attendance Alert"
    if status == "Absent":
        message = "You were marked ABSENT today. Please contact faculty."
    else:
        message = "You were marked PRESENT today. Happy Learning."

    send_email(student_email, subject, message)

    return {"message": "Attendance marked successfully"}


# -------------------------
# ATTENDANCE HISTORY
# -------------------------
@app.get("/attendance_history")
def attendance_history(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    return records


# -------------------------
# ORDER FOOD
# -------------------------
@app.post("/order_food")
def order_food(student_name: str, food_item: str, break_time: str, student_email: str, db: Session = Depends(get_db)):
    order = FoodOrder(
        student=student_name,
        food=food_item,
        time=break_time
    )

    db.add(order)
    db.commit()

    send_email(
        student_email,
        "Food Order Confirmation",
        f"Your order for {food_item} at {break_time} is confirmed."
    )

    return {"message": "Food order placed successfully"}


# -------------------------
# FOOD ORDER HISTORY
# -------------------------
@app.get("/food_order_history")
def food_order_history(db: Session = Depends(get_db)):
    orders = db.query(FoodOrder).all()
    return orders


# -------------------------
# GET STUDENT BY ROLL
# -------------------------
@app.get("/student/{roll_number}")
def get_student(roll_number: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.roll == roll_number).first()

    if student:
        return student

    return {"error": "Student not found"}

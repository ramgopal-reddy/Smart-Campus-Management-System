from fastapi import FastAPI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

from database import students, attendance_records, food_orders

app = FastAPI(title="Smart LPU Campus Management System")

# ------------------------------------------------
# SENDGRID EMAIL FUNCTION (PASSWORD-LESS)
# ------------------------------------------------
def send_email(to_email, subject, message_text):
    message = Mail(
        from_email=os.getenv("DEVELOPER_EMAIL"),
        to_emails=to_email,
        subject=subject,
        plain_text_content=message_text
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print("Email sent:", response.status_code)
    except Exception as e:
        print("Email error:", e)


# ------------------------------------------------
# STUDENT MODULE
# ------------------------------------------------
@app.post("/add_student")
def add_student(student_name: str, roll_number: str, student_email: str):
    student = {
        "name": student_name,
        "roll": roll_number,
        "email": student_email
    }
    students.append(student)
    return {"message": "Student added successfully"}


# ------------------------------------------------
# ATTENDANCE MODULE
# ------------------------------------------------
@app.post("/mark_attendance")
def mark_attendance(roll_number: str, status: str, student_email: str):
    record = {
        "roll": roll_number,
        "status": status
    }
    attendance_records.append(record)

    if status == "Absent":
        send_email(
            to_email=student_email,
            subject="Attendance Alert",
            message_text="You were marked ABSENT today. Please contact faculty."
        )
        
    if status == "Present":
        send_email(
            to_email=student_email,
            subject="Attendance Alert",
            message_text="You were marked PRESENT today. Happy Learning."
        )

    return {"message": "Attendance marked successfully"}


@app.get("/attendance_history")
def attendance_history():
    return attendance_records


# ------------------------------------------------
# FOOD PRE-ORDER MODULE
# ------------------------------------------------
@app.post("/order_food")
def order_food(student_name: str, food_item: str, break_time: str, student_email: str):
    order = {
        "student": student_name,
        "food": food_item,
        "time": break_time
    }
    food_orders.append(order)

    send_email(
        to_email=student_email,
        subject="Food Order Confirmation",
        message_text=f"Your order for {food_item} at {break_time} is confirmed."
    )

    return {"message": "Food order placed successfully"}


@app.get("/food_order_history")
def food_order_history():
    return food_orders
# ------------------------------------
# STUDENT MODULE
# ------------------------------------
@app.post("/add_student")
def add_student(student_name: str, roll_number: str, student_email: str):
    student = {
        "name": student_name,
        "roll": roll_number,
        "email": student_email
    }
    students.append(student)
    return {"message": "Student added successfully"}


# ------------------------------------
# ATTENDANCE MODULE
# ------------------------------------
@app.post("/mark_attendance")
def mark_attendance(roll_number: str, status: str, student_email: str):
    record = {
        "roll": roll_number,
        "status": status
    }
    attendance_records.append(record)

    if status == "Absent":
        send_email(
            to_email=student_email,
            message="You were marked ABSENT today. Please contact faculty."
        )

    return {"message": "Attendance marked successfully"}


@app.get("/attendance_history")
def attendance_history():
    return attendance_records

# -----------------------------
# GET STUDENT DETAILS
# -----------------------------
@app.get("/student/{roll_number}")
def get_student(roll_number: str):

    for student in students:

        if student["roll"] == roll_number:
            return student

    return {"error": "Student not found"}



# ------------------------------------
# FOOD PRE-ORDER MODULE
# ------------------------------------
@app.post("/order_food")
def order_food(student_name: str, food_item: str, break_time: str, student_email: str):
    order = {
        "student": student_name,
        "food": food_item,
        "time": break_time
    }
    food_orders.append(order)

    send_email(
        to_email=student_email,
        message=f"Your food order for {food_item} at {break_time} is confirmed."
    )

    return {"message": "Food order placed successfully"}


@app.get("/food_order_history")
def food_order_history():
    return food_orders

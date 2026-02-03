from fastapi import FastAPI
import requests
from database import students, attendance_records, food_orders, makeup_classes

app = FastAPI(title="Smart LPU Campus Management System")

# ------------------------------------
# EMAILJS CONFIG (REPLACE WITH YOURS)
# ------------------------------------
EMAILJS_SERVICE_ID = "service_studentmail"
EMAILJS_TEMPLATE_ID = "template_studentemail"
EMAILJS_PUBLIC_KEY = "kzDMTd-G5wAKcvoY-"

# ------------------------------------
# EMAIL FUNCTION (FIXED & SAFE)
# ------------------------------------
def send_email(to_email, message):
    email_data = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "template_params": {
            "to_email": to_email,
            "message": message
        }
    }

    response = requests.post(
        "https://api.emailjs.com/api/v1.0/email/send",
        json=email_data
    )

    print("EmailJS Status:", response.status_code)
    print("EmailJS Response:", response.text)


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

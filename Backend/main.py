from fastapi import FastAPI
import requests
from database import students, attendance_records, food_orders, makeup_classes

app = FastAPI(title="Smart LPU Campus Management System")

# ----------------------------------
# EMAILJS CONFIG (REPLACE VALUES)
# ----------------------------------
EMAILJS_SERVICE_ID = "service_studentmail"
EMAILJS_TEMPLATE_ID = "template_studentemail"
EMAILJS_PUBLIC_KEY = "kzDMTd-G5wAKcvoY-"

# ----------------------------------
# SIMPLE EMAIL FUNCTION
# ----------------------------------
def send_email(to_email, subject, message):
    email_data = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "template_params": {
            "to_email": to_email,
            "subject": subject,
            "message": message
        }
    }

    try:
        requests.post(
            "https://api.emailjs.com/api/v1.0/email/send",
            json=email_data
        )
    except:
        print("Email failed")


# ----------------------------------
# STUDENT MODULE
# ----------------------------------
@app.post("/add_student")
def add_student(student_name: str, roll_number: str, student_email: str):
    student = {
        "name": student_name,
        "roll": roll_number,
        "email": student_email
    }
    students.append(student)
    return {"message": "Student added successfully"}


# ----------------------------------
# ATTENDANCE MODULE
# ----------------------------------
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
            message="You have been marked ABSENT today."
        )

    return {"message": "Attendance marked successfully"}


@app.get("/absentees")
def get_absentees():
    absentees = []
    for record in attendance_records:
        if record["status"] == "Absent":
            absentees.append(record["roll"])
    return {"absent_students": absentees}


# ----------------------------------
# FOOD PRE-ORDER MODULE
# ----------------------------------
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
        message=f"Your order for {food_item} at {break_time} is confirmed."
    )

    return {"message": "Food order placed successfully"}


# ----------------------------------
# MAKE-UP CLASS MODULE
# ----------------------------------
@app.post("/schedule_makeup_class")
def schedule_makeup_class(subject_name: str, remedial_code: str):
    makeup_classes.append({
        "subject": subject_name,
        "code": remedial_code
    })
    return {"message": "Make-up class scheduled"}

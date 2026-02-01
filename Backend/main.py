# backend/main.py

from fastapi import FastAPI
from database import students, attendance_records, food_orders, makeup_classes

app = FastAPI(title="Smart LPU Campus Management System")

# -----------------------------
# Student Module
# -----------------------------
@app.post("/add_student")
def add_student(student_name: str, roll_number: str):
    student = {
        "name": student_name,
        "roll": roll_number
    }
    students.append(student)
    return {"message": "Student added successfully"}


@app.get("/students")
def get_students():
    return students


# -----------------------------
# Attendance Module
# -----------------------------
@app.post("/mark_attendance")
def mark_attendance(roll_number: str, status: str):
    attendance = {
        "roll": roll_number,
        "status": status
    }
    attendance_records.append(attendance)
    return {"message": "Attendance marked successfully"}


@app.get("/attendance")
def get_attendance():
    return attendance_records


@app.get("/absentees")
def get_absentees():
    absent_students = []

    for record in attendance_records:
        if record["status"] == "Absent":
            absent_students.append(record["roll"])

    return {"absent_students": absent_students}


# -----------------------------
# Food Pre-Order Module
# -----------------------------
@app.post("/order_food")
def order_food(student_name: str, food_item: str, break_time: str):
    order = {
        "student": student_name,
        "food": food_item,
        "time": break_time
    }
    food_orders.append(order)
    return {"message": "Food order placed successfully"}


@app.get("/food_orders")
def get_food_orders():
    return food_orders


@app.get("/food_demand")
def food_demand():
    demand_count = {}

    for order in food_orders:
        time = order["time"]
        if time in demand_count:
            demand_count[time] += 1
        else:
            demand_count[time] = 1

    return demand_count


# -----------------------------
# Make-Up Class Module
# -----------------------------
@app.post("/schedule_makeup_class")
def schedule_makeup_class(subject_name: str, remedial_code: str):
    makeup_class = {
        "subject": subject_name,
        "code": remedial_code
    }
    makeup_classes.append(makeup_class)
    return {"message": "Make-up class scheduled successfully"}


@app.post("/mark_makeup_attendance")
def mark_makeup_attendance(roll_number: str, remedial_code: str):
    record = {
        "roll": roll_number,
        "remedial_code": remedial_code
    }
    attendance_records.append(record)
    return {"message": "Make-up attendance marked successfully"}

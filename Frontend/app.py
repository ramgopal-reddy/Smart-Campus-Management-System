# frontend/app.py

import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("🏫 Smart LPU Campus Management System")

menu = st.selectbox(
    "Select Module",
    [
        "Add Student",
        "Mark Attendance",
        "View Absentees",
        "Food Pre-Order",
        "Make-Up Class"
    ]
)

# -----------------------------
# Add Student
# -----------------------------
if menu == "Add Student":
    st.header("Add Student")

    student_name = st.text_input("Student Name")
    roll_number = st.text_input("Roll Number")

    if st.button("Add Student"):
        response = requests.post(
            f"{BACKEND_URL}/add_student",
            params={
                "student_name": student_name,
                "roll_number": roll_number
            }
        )
        st.success(response.json()["message"])


# -----------------------------
# Mark Attendance
# -----------------------------
if menu == "Mark Attendance":
    st.header("Mark Attendance")

    roll_number = st.text_input("Roll Number")
    status = st.selectbox("Attendance Status", ["Present", "Absent"])

    if st.button("Submit Attendance"):
        response = requests.post(
            f"{BACKEND_URL}/mark_attendance",
            params={
                "roll_number": roll_number,
                "status": status
            }
        )
        st.success(response.json()["message"])


# -----------------------------
# View Absentees
# -----------------------------
if menu == "View Absentees":
    st.header("Absent Students")

    response = requests.get(f"{BACKEND_URL}/absentees")
    absentees = response.json()["absent_students"]

    if absentees:
        for roll in absentees:
            st.write("❌", roll)
    else:
        st.write("No absentees found")


# -----------------------------
# Food Pre-Order
# -----------------------------
if menu == "Food Pre-Order":
    st.header("Food Pre-Order System")

    student_name = st.text_input("Student Name")
    food_item = st.text_input("Food Item")
    break_time = st.selectbox("Break Time", ["10:30 AM", "1:30 PM", "4:30 PM"])

    if st.button("Place Order"):
        response = requests.post(
            f"{BACKEND_URL}/order_food",
            params={
                "student_name": student_name,
                "food_item": food_item,
                "break_time": break_time
            }
        )
        st.success(response.json()["message"])


# -----------------------------
# Make-Up Class
# -----------------------------
if menu == "Make-Up Class":
    st.header("Make-Up Class Scheduling")

    subject_name = st.text_input("Subject Name")
    remedial_code = st.text_input("Remedial Code")

    if st.button("Schedule Class"):
        response = requests.post(
            f"{BACKEND_URL}/schedule_makeup_class",
            params={
                "subject_name": subject_name,
                "remedial_code": remedial_code
            }
        )
        st.success(response.json()["message"])

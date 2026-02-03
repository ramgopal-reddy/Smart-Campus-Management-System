import streamlit as st
import requests

BACKEND_URL = "https://smart-campus-management-system-lcgz.onrender.com"

st.title("🏫 Smart LPU Campus Management System")

menu = st.selectbox(
    "Select Module",
    [
        "Add Student",
        "Mark Attendance",
        "Food Order"
    ]
)

# ----------------------------------
# ADD STUDENT
# ----------------------------------
if menu == "Add Student":
    st.header("Add Student")

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    email = st.text_input("Student Email")

    if st.button("Add Student"):
        response = requests.post(
            f"{BACKEND_URL}/add_student",
            params={
                "student_name": name,
                "roll_number": roll,
                "student_email": email
            }
        )
        st.success(response.json()["message"])


# ----------------------------------
# MARK ATTENDANCE
# ----------------------------------
if menu == "Mark Attendance":
    st.header("Mark Attendance")

    roll = st.text_input("Roll Number")
    email = st.text_input("Student Email")
    status = st.selectbox("Status", ["Present", "Absent"])

    if st.button("Submit Attendance"):
        response = requests.post(
            f"{BACKEND_URL}/mark_attendance",
            params={
                "roll_number": roll,
                "status": status,
                "student_email": email
            }
        )
        st.success(response.json()["message"])


# ----------------------------------
# FOOD ORDER
# ----------------------------------
if menu == "Food Order":
    st.header("Food Pre-Order")

    name = st.text_input("Student Name")
    email = st.text_input("Student Email")
    food = st.text_input("Food Item")
    time = st.selectbox("Break Time", ["10:30 AM", "1:30 PM", "4:30 PM"])

    if st.button("Order Food"):
        response = requests.post(
            f"{BACKEND_URL}/order_food",
            params={
                "student_name": name,
                "food_item": food,
                "break_time": time,
                "student_email": email
            }
        )
        st.success(response.json()["message"])# View Absentees
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

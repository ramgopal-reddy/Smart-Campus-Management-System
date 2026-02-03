import streamlit as st
import requests

BACKEND_URL = "https://smart-campus-management-system-lcgz.onrender.com"  # replace with Render URL after deploy

st.title("🏫 Smart LPU Campus Management System")

menu = st.selectbox(
    "Select Module",
    [
        "Add Student",
        "Mark Attendance",
        "Attendance History",
        "Food Order",
        "Food Order History"
    ]
)

# ------------------------------------
# ADD STUDENT
# ------------------------------------
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


# ------------------------------------
# MARK ATTENDANCE
# ------------------------------------
if menu == "Mark Attendance":
    st.header("Mark Attendance")

    roll = st.text_input("Roll Number")
    email = st.text_input("Student Email")
    status = st.selectbox("Attendance Status", ["Present", "Absent"])

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


# ------------------------------------
# ATTENDANCE HISTORY
# ------------------------------------
if menu == "Attendance History":
    st.header("Attendance History")

    response = requests.get(f"{BACKEND_URL}/attendance_history")
    records = response.json()

    if records:
        for record in records:
            st.write(f"Roll: {record['roll']} | Status: {record['status']}")
    else:
        st.info("No attendance records found")


# ------------------------------------
# FOOD ORDER
# ------------------------------------
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
        st.success(response.json()["message"])


# ------------------------------------
# FOOD ORDER HISTORY
# ------------------------------------
if menu == "Food Order History":
    st.header("Food Order History")

    response = requests.get(f"{BACKEND_URL}/food_order_history")
    orders = response.json()

    if orders:
        for order in orders:
            st.write(
                f"Student: {order['student']} | Food: {order['food']} | Time: {order['time']}"
            )
    else:
        st.info("No food orders found")

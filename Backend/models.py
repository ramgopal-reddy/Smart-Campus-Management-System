from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


# -------------------------
# STUDENT MODEL
# -------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    roll = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    attendance_records = relationship("Attendance", back_populates="student")
    food_orders = relationship("FoodOrder", back_populates="student_obj")


# -------------------------
# ATTENDANCE MODEL
# -------------------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    roll = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # "Present" or "Absent"
    date = Column(DateTime, default=datetime.now, index=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")


# -------------------------
# FOOD ORDER MODEL
# -------------------------
class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(Integer, primary_key=True, index=True)
    student = Column(String(100), nullable=False)
    food = Column(String(100), nullable=False)
    time = Column(String(50), nullable=False)
    date = Column(DateTime, default=datetime.now, index=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    student_obj = relationship("Student", back_populates="food_orders")


# -------------------------
# FACULTY MODEL
# -------------------------
class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=False, index=True)
    designation = Column(String(100), nullable=False)
    specialization = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# -------------------------
# CLASSROOM MODEL
# -------------------------
class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), unique=True, nullable=False, index=True)
    building = Column(String(50), nullable=False, index=True)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    equipment = Column(Text, nullable=True)
    status = Column(String(20), default="Available", index=True)  # "Available", "Occupied", "Maintenance"
    room_type = Column(String(50), nullable=False, index=True)  # "Lecture", "Lab", "Seminar", "Conference"
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# -------------------------
# BLOCK MODEL
# -------------------------
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    total_floors = Column(Integer, nullable=False)
    address = Column(Text, nullable=True)
    facilities = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    classrooms = relationship("Classroom", back_populates="block")


# -------------------------
# COURSE MODEL (Optional for future expansion)
# -------------------------
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    credits = Column(Integer, nullable=False)
    department = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)


# -------------------------
# TIMETABLE MODEL (Optional for future expansion)
# -------------------------
class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    course_code = Column(String(20), ForeignKey("courses.code"), nullable=False)
    day_of_week = Column(String(20), nullable=False, index=True)  # "Monday", "Tuesday", etc.
    start_time = Column(String(10), nullable=False)  # "09:00", "10:00", etc.
    end_time = Column(String(10), nullable=False)
    semester = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    classroom = relationship("Classroom")
    faculty = relationship("Faculty")
    course = relationship("Course")


# -------------------------
# NOTIFICATION MODEL (Optional for future expansion)
# -------------------------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    recipient_type = Column(String(20), nullable=False, index=True)  # "Student", "Faculty", "All"
    recipient_id = Column(Integer, nullable=True)  # Optional specific recipient
    is_read = Column(String(10), default="False", index=True)
    priority = Column(String(20), default="Normal")  # "Low", "Normal", "High", "Urgent"
    created_at = Column(DateTime, default=datetime.now, index=True)
    expires_at = Column(DateTime, nullable=True)


# -------------------------
# SYSTEM LOG MODEL (Optional for future expansion)
# -------------------------
class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # "Student", "Faculty", "Classroom", etc.
    entity_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)  # Who performed the action
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, index=True)

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

# ==========================================================
# STUDENT
# ==========================================================
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    roll = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=False)

# ==========================================================
# REGULAR ATTENDANCE
# ==========================================================
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    roll = Column(String, nullable=False)
    status = Column(String, nullable=False)

# ==========================================================
# FOOD ORDER
# ==========================================================
class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(Integer, primary_key=True, index=True)
    student = Column(String, nullable=False)
    food = Column(String, nullable=False)
    time = Column(String, nullable=False)

# ==========================================================
# BLOCK
# ==========================================================
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

# ==========================================================
# CLASSROOM
# ==========================================================
class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)

# ==========================================================
# COURSE
# ==========================================================
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    weekly_hours = Column(Integer, nullable=False)

# ==========================================================
# FACULTY
# ==========================================================
class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

# ==========================================================
# FACULTY COURSE ASSIGNMENT
# ==========================================================
class FacultyCourse(Base):
    __tablename__ = "faculty_courses"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    assigned_hours = Column(Integer, nullable=False)

# ==========================================================
# MAKE-UP CLASS MODULE
# ==========================================================

class MakeupClass(Base):
    __tablename__ = "makeup_classes"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    scheduled_time = Column(String, nullable=False)
    remedial_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MakeupAttendance(Base):
    __tablename__ = "makeup_attendance"

    id = Column(Integer, primary_key=True, index=True)
    makeup_class_id = Column(Integer, ForeignKey("makeup_classes.id"), nullable=False)
    roll = Column(String, nullable=False)
    status = Column(String, nullable=False)

# ==========================================================
# AUTHENTICATION TABLE
# ==========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="student")  # admin / faculty / student
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

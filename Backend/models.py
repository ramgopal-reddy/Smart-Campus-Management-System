from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# -------------------------
# STUDENT
# -------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    roll = Column(String, unique=True, index=True)
    email = Column(String)

# -------------------------
# REGULAR ATTENDANCE
# -------------------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    roll = Column(String)
    status = Column(String)

# -------------------------
# FOOD ORDER
# -------------------------
class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(Integer, primary_key=True, index=True)
    student = Column(String)
    food = Column(String)
    time = Column(String)

# -------------------------
# BLOCK
# -------------------------
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

# -------------------------
# CLASSROOM
# -------------------------
class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String)
    capacity = Column(Integer)
    block_id = Column(Integer, ForeignKey("blocks.id"))

# -------------------------
# COURSE
# -------------------------
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String)
    course_name = Column(String)
    weekly_hours = Column(Integer)

# -------------------------
# FACULTY
# -------------------------
class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)

# -------------------------
# FACULTY COURSE ASSIGNMENT
# -------------------------
class FacultyCourse(Base):
    __tablename__ = "faculty_courses"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    assigned_hours = Column(Integer)

# ==========================================================
# NEW MAKE-UP CLASS MODULE
# ==========================================================

# -------------------------
# MAKEUP CLASS
# -------------------------
class MakeupClass(Base):
    __tablename__ = "makeup_classes"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    scheduled_time = Column(String)
    remedial_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# -------------------------
# MAKEUP ATTENDANCE
# -------------------------
class MakeupAttendance(Base):
    __tablename__ = "makeup_attendance"

    id = Column(Integer, primary_key=True, index=True)
    makeup_class_id = Column(Integer, ForeignKey("makeup_classes.id"))
    roll = Column(String)
    status = Column(String)

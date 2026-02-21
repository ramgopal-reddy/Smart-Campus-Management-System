from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    roll = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    roll = Column(String, nullable=False)
    status = Column(String, nullable=False)


class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(Integer, primary_key=True, index=True)
    student = Column(String, nullable=False)
    food = Column(String, nullable=False)
    time = Column(String, nullable=False)


# -------------------------
# BLOCK
# -------------------------
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    classrooms = relationship("Classroom", back_populates="block")


# -------------------------
# CLASSROOM
# -------------------------
class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String)
    capacity = Column(Integer)

    block_id = Column(Integer, ForeignKey("blocks.id"))
    block = relationship("Block", back_populates="classrooms")


# -------------------------
# COURSE
# -------------------------
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True)
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

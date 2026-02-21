from sqlalchemy import Column, Integer, String
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

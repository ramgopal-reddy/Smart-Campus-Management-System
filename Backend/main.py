from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

from database import SessionLocal, engine
from models import Base, Student, Attendance, FoodOrder

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart LPU Campus Management System")


# -------------------------
# CORS CONFIG (REMOVE "*" IN PRODUCTION)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://your-frontend-domain.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# DATABASE DEPENDENCY
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# PYDANTIC SCHEMAS
# -------------------------
class StudentCreate(BaseModel):
    student_name: str
    roll_number: str
    student_email: str

class StudentUpdate(BaseModel):
    student_name: Optional[str] = None
    student_email: Optional[str] = None

class AttendanceCreate(BaseModel):
    roll_number: str
    status: str
    student_email: str

class FoodOrderCreate(BaseModel):
    student_name: str
    food_item: str
    break_time: str
    student_email: str

class FacultyCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    department: str
    designation: str
    specialization: Optional[str] = None

class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    specialization: Optional[str] = None

class ClassroomCreate(BaseModel):
    room_number: str
    building: str
    floor: int
    capacity: int
    equipment: Optional[str] = None
    status: str = "Available"
    room_type: str

class ClassroomUpdate(BaseModel):
    room_number: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    equipment: Optional[str] = None
    status: Optional[str] = None
    room_type: Optional[str] = None

class BlockCreate(BaseModel):
    name: str
    description: Optional[str] = None
    total_floors: int
    address: Optional[str] = None
    facilities: Optional[str] = None

class BlockUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    total_floors: Optional[int] = None
    address: Optional[str] = None
    facilities: Optional[str] = None


# -------------------------
# SEND EMAIL FUNCTION
# -------------------------
def send_email(to_email: str, subject: str, message_text: str):
    try:
        message = Mail(
            from_email=os.getenv("DEVELOPER_EMAIL"),
            to_emails=to_email,
            subject=subject,
            plain_text_content=message_text
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)

    except Exception as e:
        print("Email error:", e)


# -------------------------
# STUDENT ENDPOINTS
# -------------------------
@app.post("/add_student")
def add_student(data: StudentCreate, db: Session = Depends(get_db)):
    existing_student = db.query(Student).filter(Student.roll == data.roll_number).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student with this roll number already exists")

    student = Student(
        name=data.student_name,
        roll=data.roll_number,
        email=data.student_email
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return {"message": "Student added successfully", "student_id": student.id}

@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "roll": s.roll,
            "email": s.email
        }
        for s in students
    ]

@app.get("/student/{roll_number}")
def get_student(roll_number: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.roll == roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "id": student.id,
        "name": student.name,
        "roll": student.roll,
        "email": student.email
    }

@app.put("/student/{student_id}")
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if data.student_name:
        student.name = data.student_name
    if data.student_email:
        student.email = data.student_email

    db.commit()
    return {"message": "Student updated successfully"}

@app.delete("/student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


# -------------------------
# ATTENDANCE ENDPOINTS
# -------------------------
@app.post("/mark_attendance")
def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.roll == data.roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    record = Attendance(
        roll=data.roll_number,
        status=data.status,
        date=datetime.now()
    )

    db.add(record)
    db.commit()

    subject = "Attendance Alert"
    if data.status.lower() == "absent":
        message = "You were marked ABSENT today. Please contact faculty."
    else:
        message = "You were marked PRESENT today. Happy Learning."

    send_email(data.student_email, subject, message)
    return {"message": "Attendance marked successfully"}

@app.get("/attendance_history")
def attendance_history(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    return [
        {
            "id": r.id,
            "roll": r.roll,
            "status": r.status,
            "date": r.date.isoformat() if r.date else None
        }
        for r in records
    ]


# -------------------------
# FOOD ORDER ENDPOINTS
# -------------------------
@app.post("/order_food")
def order_food(data: FoodOrderCreate, db: Session = Depends(get_db)):
    order = FoodOrder(
        student=data.student_name,
        food=data.food_item,
        time=data.break_time,
        date=datetime.now()
    )

    db.add(order)
    db.commit()

    send_email(
        data.student_email,
        "Food Order Confirmation",
        f"Your order for {data.food_item} at {data.break_time} is confirmed."
    )

    return {"message": "Food order placed successfully", "order_id": order.id}

@app.get("/food_order_history")
def food_order_history(db: Session = Depends(get_db)):
    orders = db.query(FoodOrder).all()
    return [
        {
            "id": o.id,
            "student": o.student,
            "food": o.food,
            "time": o.time,
            "date": o.date.isoformat() if o.date else None
        }
        for o in orders
    ]


# -------------------------
# FACULTY ENDPOINTS
# -------------------------
@app.post("/add_faculty")
def add_faculty(data: FacultyCreate, db: Session = Depends(get_db)):
    # Check if faculty email already exists
    existing_faculty = db.query(Faculty).filter(Faculty.email == data.email).first()
    if existing_faculty:
        raise HTTPException(status_code=400, detail="Faculty with this email already exists")

    faculty = Faculty(
        name=data.name,
        email=data.email,
        phone=data.phone,
        department=data.department,
        designation=data.designation,
        specialization=data.specialization
    )

    db.add(faculty)
    db.commit()
    db.refresh(faculty)

    return {"message": "Faculty added successfully", "faculty_id": faculty.id}

@app.get("/faculty_list")
def get_faculty_list(db: Session = Depends(get_db)):
    faculty_list = db.query(Faculty).all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "email": f.email,
            "phone": f.phone,
            "department": f.department,
            "designation": f.designation,
            "specialization": f.specialization
        }
        for f in faculty_list
    ]

@app.get("/faculty/{faculty_id}")
def get_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {
        "id": faculty.id,
        "name": faculty.name,
        "email": faculty.email,
        "phone": faculty.phone,
        "department": faculty.department,
        "designation": faculty.designation,
        "specialization": faculty.specialization
    }

@app.put("/faculty/{faculty_id}")
def update_faculty(faculty_id: int, data: FacultyUpdate, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    # Update fields if provided
    if data.name:
        faculty.name = data.name
    if data.email:
        faculty.email = data.email
    if data.phone:
        faculty.phone = data.phone
    if data.department:
        faculty.department = data.department
    if data.designation:
        faculty.designation = data.designation
    if data.specialization:
        faculty.specialization = data.specialization

    db.commit()
    return {"message": "Faculty updated successfully"}

@app.delete("/faculty/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    db.delete(faculty)
    db.commit()
    return {"message": "Faculty deleted successfully"}


# -------------------------
# CLASSROOM ENDPOINTS
# -------------------------
@app.post("/add_classroom")
def add_classroom(data: ClassroomCreate, db: Session = Depends(get_db)):
    # Check if classroom number already exists
    existing_classroom = db.query(Classroom).filter(Classroom.room_number == data.room_number).first()
    if existing_classroom:
        raise HTTPException(status_code=400, detail="Classroom with this number already exists")

    classroom = Classroom(
        room_number=data.room_number,
        building=data.building,
        floor=data.floor,
        capacity=data.capacity,
        equipment=data.equipment,
        status=data.status,
        room_type=data.room_type
    )

    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    return {"message": "Classroom added successfully", "classroom_id": classroom.id}

@app.get("/classroom_list")
def get_classroom_list(db: Session = Depends(get_db)):
    classrooms = db.query(Classroom).all()
    return [
        {
            "id": c.id,
            "room_number": c.room_number,
            "building": c.building,
            "floor": c.floor,
            "capacity": c.capacity,
            "equipment": c.equipment,
            "status": c.status,
            "room_type": c.room_type
        }
        for c in classrooms
    ]

@app.get("/classroom/{classroom_id}")
def get_classroom(classroom_id: int, db: Session = Depends(get_db)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    return {
        "id": classroom.id,
        "room_number": classroom.room_number,
        "building": classroom.building,
        "floor": classroom.floor,
        "capacity": classroom.capacity,
        "equipment": classroom.equipment,
        "status": classroom.status,
        "room_type": classroom.room_type
    }

@app.put("/classroom/{classroom_id}")
def update_classroom(classroom_id: int, data: ClassroomUpdate, db: Session = Depends(get_db)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # Update fields if provided
    if data.room_number:
        classroom.room_number = data.room_number
    if data.building:
        classroom.building = data.building
    if data.floor:
        classroom.floor = data.floor
    if data.capacity:
        classroom.capacity = data.capacity
    if data.equipment:
        classroom.equipment = data.equipment
    if data.status:
        classroom.status = data.status
    if data.room_type:
        classroom.room_type = data.room_type

    db.commit()
    return {"message": "Classroom updated successfully"}

@app.delete("/classroom/{classroom_id}")
def delete_classroom(classroom_id: int, db: Session = Depends(get_db)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    db.delete(classroom)
    db.commit()
    return {"message": "Classroom deleted successfully"}


# -------------------------
# BLOCK ENDPOINTS
# -------------------------
@app.post("/add_block")
def add_block(data: BlockCreate, db: Session = Depends(get_db)):
    # Check if block name already exists
    existing_block = db.query(Block).filter(Block.name == data.name).first()
    if existing_block:
        raise HTTPException(status_code=400, detail="Block with this name already exists")

    block = Block(
        name=data.name,
        description=data.description,
        total_floors=data.total_floors,
        address=data.address,
        facilities=data.facilities
    )

    db.add(block)
    db.commit()
    db.refresh(block)

    return {"message": "Block added successfully", "block_id": block.id}

@app.get("/block_list")
def get_block_list(db: Session = Depends(get_db)):
    blocks = db.query(Block).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "total_floors": b.total_floors,
            "address": b.address,
            "facilities": b.facilities
        }
        for b in blocks
    ]

@app.get("/block/{block_id}")
def get_block(block_id: int, db: Session = Depends(get_db)):
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    return {
        "id": block.id,
        "name": block.name,
        "description": block.description,
        "total_floors": block.total_floors,
        "address": block.address,
        "facilities": block.facilities
    }

@app.put("/block/{block_id}")
def update_block(block_id: int, data: BlockUpdate, db: Session = Depends(get_db)):
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    # Update fields if provided
    if data.name:
        block.name = data.name
    if data.description:
        block.description = data.description
    if data.total_floors:
        block.total_floors = data.total_floors
    if data.address:
        block.address = data.address
    if data.facilities:
        block.facilities = data.facilities

    db.commit()
    return {"message": "Block updated successfully"}

@app.delete("/block/{block_id}")
def delete_block(block_id: int, db: Session = Depends(get_db)):
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    db.delete(block)
    db.commit()
    return {"message": "Block deleted successfully"}


# -------------------------
# DASHBOARD STATISTICS
# -------------------------
@app.get("/dashboard_stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_students = db.query(Student).count()
    total_faculty = db.query(Faculty).count()
    total_classrooms = db.query(Classroom).count()
    total_blocks = db.query(Block).count()
    
    # Today's attendance
    from datetime import date
    today = date.today()
    today_attendance = db.query(Attendance).filter(Attendance.date >= today).count()
    
    # Today's food orders
    today_orders = db.query(FoodOrder).filter(FoodOrder.date >= today).count()
    
    # Available classrooms
    available_classrooms = db.query(Classroom).filter(Classroom.status == "Available").count()
    
    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_classrooms": total_classrooms,
        "total_blocks": total_blocks,
        "today_attendance": today_attendance,
        "today_food_orders": today_orders,
        "available_classrooms": available_classrooms
    }


# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Smart Campus API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

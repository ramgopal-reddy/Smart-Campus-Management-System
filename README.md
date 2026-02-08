# 🏫 Smart AI Campus Management System

A full-stack Smart Campus Management System built with **FastAPI, Streamlit, and Face Recognition AI**. This project combines web development, AI automation, and cloud deployment into a practical real-world application.

---

## 🚀 Features

* ✅ Student registration system
* ✅ Smart attendance management
* ✅ AI face recognition attendance (local module)
* ✅ Food pre-order system
* ✅ Attendance & order history tracking
* ✅ Automated email notifications (SendGrid)
* ✅ Cloud deployment with Render & Streamlit Cloud

---

## 🧠 System Architecture

```
Streamlit Frontend (Cloud)
        ↓
FastAPI Backend (Render)
        ↓
Email Notifications

Local Face Recognition Module
        ↓
Backend API Attendance Update
```

The system separates UI, backend logic, and AI processing for better scalability and performance.

---

## 🛠 Tech Stack

**Backend**

* FastAPI
* Python 3.10
* SendGrid API

**Frontend**

* Streamlit

**AI Module**

* OpenCV
* face_recognition (dlib)

**Deployment**

* Render (Backend)
* Streamlit Cloud (Frontend)
* GitHub (Version Control)

---

## 📁 Project Structure

```
smart-campus/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   └── requirements.txt
│
├── face_ai/
│   ├── face_app.py
│   └── known_faces/
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```
git clone https://github.com/yourusername/smart-campus-project.git
cd smart-campus-project
```

---

### 2. Create Virtual Environment (Python 3.10)

```
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3. Install Dependencies

#### Backend

```
cd backend
pip install -r requirements.txt
```

#### Frontend

```
cd ../frontend
pip install -r requirements.txt
```

#### Face AI Module

```
cd ../face_ai
pip install opencv-python face-recognition streamlit numpy requests
```

---

## ▶ Running the Project

### Start Backend

```
cd backend
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### Start Frontend

```
cd frontend
streamlit run app.py
```

---

### Start Face Recognition Module

```
cd face_ai
streamlit run face_app.py
```

Place student face images inside:

```
face_ai/known_faces/
```

Image filename = student roll number.

---

## ☁ Deployment

* Backend deployed on **Render**
* Frontend deployed on **Streamlit Cloud**
* Environment variables used for secure email API keys

---

## 📚 Key Learnings

This project demonstrates:

* Full-stack system architecture
* AI integration with web APIs
* Cloud deployment workflows
* Environment & dependency management
* Real-world debugging and problem solving

---

## 🔗 Project Links

GitHub: [https://github.com/ramgopal-reddy/Smart-Campus-Management-System](https://github.com/ramgopal-reddy/Smart-Campus-Management-System)

Portfolio: [https://ramgopalreddy.vercel.app/](https://ramgopalreddy.vercel.app/)

LinkedIn: [https://www.linkedin.com/in/ramgopal-reddy/](https://www.linkedin.com/in/ramgopal-reddy/)

---

## 📄 License

This project is open-source and available for educational and learning purposes.

---

⭐ If you found this project useful, consider starring the repository!

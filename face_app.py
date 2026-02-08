import streamlit as st
import cv2
import face_recognition
import numpy as np
import requests
import os

BACKEND_URL = "https://your_backend_url.onrender.com"

st.title("Face Recognition Attendance")

# -----------------------------
# LOAD KNOWN FACES
# -----------------------------
known_encodings = []
known_rolls = []

folder = "known_faces"

for file in os.listdir(folder):

    path = os.path.join(folder, file)

    image = face_recognition.load_image_file(path)

    enc = face_recognition.face_encodings(image)

    if len(enc) == 0:
        st.warning(f"No face found in {file}")
        continue

    known_encodings.append(enc[0])
    known_rolls.append(file.split(".")[0])

# -----------------------------
# CAMERA INPUT
# -----------------------------
photo = st.camera_input("Take Attendance Photo")

if photo is not None:

    # Convert to numpy safely
    bytes_data = np.frombuffer(photo.read(), np.uint8)
    frame = cv2.imdecode(bytes_data, cv2.IMREAD_COLOR)

    if frame is None:
        st.error("Camera image failed to load")
        st.stop()

    # Resize for stability
    frame = cv2.resize(frame, (640, 480))

    # Convert BGR → RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Ensure contiguous memory
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb)

    if len(face_locations) == 0:
        st.error("No face detected")
        st.stop()

    # Encode faces
    encodings = face_recognition.face_encodings(rgb, face_locations)

    for face in encodings:

        matches = face_recognition.compare_faces(
            known_encodings,
            face
        )

        if True in matches:

            index = matches.index(True)
            roll = known_rolls[index]

            # -----------------------------
            # GET STUDENT INFO
            # -----------------------------
            student = requests.get(
                f"{BACKEND_URL}/student/{roll}"
            ).json()

            if "error" in student:
                st.error("Student not found in backend")
                st.stop()

            email = student["email"]
            name = student["name"]

            # -----------------------------
            # MARK ATTENDANCE
            # -----------------------------
            requests.post(
                f"{BACKEND_URL}/mark_attendance",
                params={
                    "roll_number": roll,
                    "status": "Present",
                    "student_email": email
                }
            )

            st.success(f"✅ Attendance marked for {name} ({roll})")

        else:
            st.error("❌ Face not recognized")

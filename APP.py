import numpy as np
import pickle
import streamlit as st
import pyrebase
from datetime import datetime

# ==================== Firebase Setup ====================
@st.cache_resource
def init_firebase():
    firebase_config = {
        "apiKey": st.secrets["firebase"]["apiKey"],
        "authDomain": st.secrets["firebase"]["authDomain"],
        "databaseURL": st.secrets["firebase"]["databaseURL"],
        "projectId": st.secrets["firebase"]["projectId"],
        "storageBucket": st.secrets["firebase"]["storageBucket"],
        "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
        "appId": st.secrets["firebase"]["appId"]
    }
    firebase = pyrebase.initialize_app(firebase_config)
    return firebase.database()

# Initialize DB
try:
    db = init_firebase()
    st.sidebar.success("Firebase Connected")
except Exception as e:
    st.sidebar.error("Firebase connection failed")
    db = None

# ==================== Load Model ====================
try:
    with open('Saving.pkl', 'rb') as f:
        Model = pickle.load(f)
    st.success("Model loaded successfully! 🎯")
except Exception as e:
    st.error("Model failed to load. Check file path.")
    st.stop()

# ==================== Streamlit UI ====================
st.title("Student Placement Prediction")
st.write("Fill the details below to predict placement outcome.")

IQ = st.number_input("IQ", min_value=50, max_value=200, step=1)
intern = st.selectbox("Internship Experience", ["Yes", "No"])
Com = st.number_input("Communication Skills (out of 10)", min_value=0.0, max_value=10.0, step=0.1)
Proj = st.number_input("Projects Completed", min_value=0, max_value=50, step=1)
Sem = st.number_input("Previous Semester Marks (%)", min_value=0.0, max_value=100.0, step=0.1)

# Convert internship to binary
intern_value = 1 if intern == "Yes" else 0

# ==================== Prediction & Logging ====================
if st.button("Predict Placement"):
    try:
        # Prepare input
        Input = np.array([[IQ, intern_value, Com, Proj, Sem]])
        Pred = Model.predict(Input)
        result = Pred[0]  # "Placed" or "Not Placed"

        # Display result
        st.success(f"**Prediction:** The student will be **{result}**")

        # === Log to Firebase ===
        if db:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iq": float(IQ),
                "internship": intern,
                "communication_skills": float(Com),
                "projects_completed": int(Proj),
                "prev_sem_marks": float(Sem),
                "prediction": result,
                "model_version": "v1.0"  # Optional: track model versions
            }
            try:
                db.child("placement_predictions").push(log_entry)
                st.toast("Prediction logged to Firebase!", icon="✅")
            except Exception as log_error:
                st.warning("Prediction made, but failed to log to Firebase.")
        else:
            st.warning("Firebase not connected — prediction not logged.")

    except Exception as e:
        st.error(f"Prediction failed: {e}")

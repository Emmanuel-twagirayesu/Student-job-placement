import numpy as np
import pickle
import streamlit as st
import pyrebase
from datetime import datetime

# ==================== Page Config ====================
st.set_page_config(
    page_title="Student Placement Predictor",
    page_icon="Graduation Cap",
    layout="centered"
)

# ==================== Firebase Init ====================
@st.cache_resource
def init_firebase():
    try:
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
    except Exception as e:
        st.error("Firebase connection failed. Check Streamlit secrets.")
        return None

# Initialize DB
db = init_firebase()

# ==================== Load Model ====================
try:
    with open('Saving.pkl', 'rb') as f:
        Model = pickle.load(f)
    st.success("Model loaded successfully!")
except Exception as e:
    st.error("Failed to load model. Ensure 'Saving.pkl' is in repo root.")
    st.stop()

# ==================== UI ====================
st.title("Student Placement Prediction")
st.markdown("### Enter student details to predict placement")

col1, col2 = st.columns(2)

with col1:
    IQ = st.number_input("IQ", min_value=50, max_value=200, value=120, step=1)
    Com = st.number_input("Communication Skills (out of 10)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    Proj = st.number_input("Projects Completed", min_value=0, max_value=50, value=5, step=1)

with col2:
    intern = st.selectbox("Internship Experience", ["Yes", "No"])
    Sem = st.number_input("Previous Semester Marks (%)", min_value=0.0, max_value=100.0, value=85.0, step=0.1)

intern_value = 1 if intern == "Yes" else 0

# ==================== Predict & Log ====================
if st.button("Predict Placement", type="primary", use_container_width=True):
    with st.spinner("Predicting..."):
        try:
            Input = np.array([[IQ, intern_value, Com, Proj, Sem]], dtype=np.float32)
            Pred = Model.predict(Input)
            result = str(Pred[0])

            # Show result
            if "Placed" in result:
                st.balloons()
                st.success(f"**Prediction:** The student will be **{result}**")
            else:
                st.warning(f"**Prediction:** The student will **{result}**")

            # Log to Firebase
            if db:
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "iq": float(IQ),
                    "internship": intern,
                    "communication_skills": float(Com),
                    "projects_completed": int(Proj),
                    "prev_sem_marks": float(Sem),
                    "prediction": result,
                    "model_version": "v1.0"
                }
                try:
                    db.child("placement_predictions").push(log_entry)
                    st.toast("Logged to Firebase!", icon="Success")
                except:
                    st.warning("Failed to log prediction.")
            else:
                st.info("Firebase not connected.")

        except Exception as e:
            st.error(f"Error: {e}")

# ==================== Footer ====================
st.markdown("---")
st.caption("Powered by Streamlit + Firebase | Secure & Logged")

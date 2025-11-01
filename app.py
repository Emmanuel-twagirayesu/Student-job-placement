import numpy as np
import pickle
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# ==================== Page Config ====================
st.set_page_config(page_title="Student Placement Predictor", page_icon="Graduation Cap", layout="centered")

# ==================== Firebase Init ====================
if not firebase_admin._apps:
    try:
        cred_dict = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
        }
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://mind-in-prediction-default-rtdb.firebaseio.com'
        })
        st.sidebar.success("Firebase Connected")
    except Exception as e:
        st.sidebar.error("Firebase failed. Check secrets.")
        db_ref = None
else:
    db_ref = db.reference()

# ==================== Load Model ====================
try:
    with open('Saving.pkl', 'rb') as f:
        Model = pickle.load(f)
    st.success("Model loaded!")
except Exception as e:
    st.error("Model not found. Upload Saving.pkl")
    st.stop()

# ==================== UI ====================
st.title("Student Placement Prediction")
st.markdown("Enter details to predict placement outcome")

col1, col2 = st.columns(2)
with col1:
    IQ = st.number_input("IQ", 50, 200, 120)
    Com = st.number_input("Communication Skills (0-10)", 0.0, 10.0, 7.0, 0.1)
    Proj = st.number_input("Projects Completed", 0, 50, 5)
with col2:
    intern = st.selectbox("Internship", ["Yes", "No"])
    Sem = st.number_input("Prev Sem Marks (%)", 0.0, 100.0, 85.0, 0.1)

intern_value = 1 if intern == "Yes" else 0

# ==================== Predict & Log ====================
if st.button("Predict Placement", type="primary", use_container_width=True):
    with st.spinner("Predicting..."):
        try:
            Input = np.array([[IQ, intern_value, Com, Proj, Sem]])
            Pred = Model.predict(Input)
            result = str(Pred[0])

            if "Placed" in result:
                st.balloons()
                st.success(f"**Prediction:** {result}")
            else:
                st.warning(f"**Prediction:** {result}")

            # Log to Firebase
            if 'db_ref' in locals() and db_ref:
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "iq": IQ,
                    "internship": intern,
                    "communication": Com,
                    "projects": Proj,
                    "sem_marks": Sem,
                    "prediction": result
                }
                db_ref.child("predictions").push(log_entry)
                st.toast("Logged to Firebase!", icon="Success")
        except Exception as e:
            st.error(f"Error: {e}")

st.caption("Powered by Streamlit + Firebase")

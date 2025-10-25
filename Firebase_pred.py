import streamlit as st
import numpy as np
import pickle
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz

# Initialize Firebase (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate('path/to/serviceAccountKey.json')  # Update path
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Load the model
try:
    with open('Saving_1.pkl', 'rb') as f:
        model = pickle.load(f)
    st.info("✅ Model loaded successfully")
except Exception as e:
    st.error(f"❌ Model failed to load: {e}")
    st.stop()

# Log prediction to Firestore
def log_prediction(marks, intern_status, project, prediction):
    try:
        db.collection('predictions').add({
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'semester_marks': float(marks),
            'internship_status': int(intern_status),
            'projects_conducted': float(project),
            'prediction': str(prediction),  # Ensure string for Firestore
            'app': 'college_placement'
        })
        st.info("📝 Prediction logged to Firestore")
    except Exception as e:
        st.warning(f"⚠️ Failed to log prediction: {e}")

# Streamlit UI
st.title("🏫 College Student Placement Prediction")
st.write("Fill the following:")

marks = st.number_input("Semester Marks", value=0.0, min_value=0.0, max_value=100.0, step=0.1)
intern = st.selectbox("Internship", ['Yes', 'No'])
project = st.number_input("Projects Conducted", value=0.0, min_value=0.0, step=1.0)

# Convert internship status
intern_status = 1 if intern == 'Yes' else 0

# Predict button
if st.button('Predict'):
    # Prepare input
    input_data = np.array([[marks, intern_status, project]])
    
    # Make prediction
    try:
        pred = model.predict(input_data)
        st.success(f'👨‍🎓 Student should be {pred[0]}')
        
        # Log to Firestore
        log_prediction(marks, intern_status, project, pred[0])
    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")

import streamlit as st
import numpy as np


import pickle
try:
    with open('Saving_1.pkl','rb')as f:
        model=pickle.load(f)
    print("Model Loaded well")
except:
    print("Model Not loaded")
    
    
st.title("🏫College student placement prediction")
st.write("Fill the following:")
Marks=st.number_input("Semesiter marks",value=0.0)
Intern=st.selectbox("Internship",['Yes','No'])
Project=st.number_input("Project conducted",value=0.0)

if Intern=='yes':
    intern_status=1 
else:
    intern_status=0
    
if st.button('Predict'):
    input_=np.array([[Marks,intern_status,Project]])
    Pred=model.predict(input_)

    st.success(f'👨‍🎓 Student should be {Pred[0]}')


import numpy as np
import pickle 
import streamlit as st
try:
    with open('Saving.pkl','rb') as f:
        Model=pickle.load(f)    
        print("Model Loaded well")
    
    #'IQ','Internship_Experience','Communication_Skills','Projects_Completed','Prev_Sem_Result_%']]
    st.title("Student Placement Prediction")
    st.write("Fill the following to get either placed or not")
    IQ=st.number_input("IQ")
    intern=st.selectbox("Internship attended",["Yes","No"])
    Com=st.number_input("Communication Skills")
    Proj=st.number_input("Project conducted")
    Sem=st.number_input("Previous semester marks (%)")
    
    value=0
    if intern=="Yes":
        value=1
    if intern=="No":
        value=0
    
    if st.button("Predict"):
        Input=np.array([[IQ,value,Com,Proj,Sem]])
        Pred=Model.predict(Input)
        st.success(f"The student should be {Pred[0]}")
except:

    print("Model Not loaded well")

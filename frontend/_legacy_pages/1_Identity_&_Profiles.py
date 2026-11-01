import streamlit as st
import pandas as pd
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, page_header, check_login

st.set_page_config(page_title="Identity", page_icon="🆔")
apply_theme()
check_login()
page_header("Identity & Profiles", "🆔", "Manage persons, patients, and doctors.")

tab1, tab2, tab3 = st.tabs(["Register Person", "Doctor Lookup", "Patient Lookup"])

with tab1:
    with st.form("create_person"):
        st.subheader("New Registration")
        col1, col2 = st.columns(2)
        full_name = col1.text_input("Full Name")
        dob = col2.date_input("Date of Birth")
        gender = col1.selectbox("Gender", ["Male", "Female", "Other"])
        phone = col2.text_input("Phone")
        email = st.text_input("Email")
        
        if st.form_submit_button("Create Person"):
            payload = {"full_name": full_name, "date_of_birth": str(dob), "gender": gender, "phone": phone, "email": email}
            res = api_request("POST", "/identity/persons", json=payload)
            if res.status_code == 201:
                st.success(f"✅ Person created! ID: {res.json()['person_id']}")
            else:
                st.error(f"Error: {res.text}")

with tab2:
    doc_id = st.number_input("Enter Doctor ID", min_value=1, step=1)
    if st.button("Fetch Doctor"):
        res = api_request("GET", f"/identity/doctors/{doc_id}")
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.warning("Doctor not found.")

with tab3:
    pat_id = st.number_input("Enter Patient ID", min_value=1, step=1)
    if st.button("Fetch Patient"):
        res = api_request("GET", f"/identity/patients/{pat_id}")
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.warning("Patient not found.")
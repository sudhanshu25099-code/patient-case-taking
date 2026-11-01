import streamlit as st
import pandas as pd
from datetime import date, time
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, page_header, check_login

st.set_page_config(page_title="Appointments", page_icon="📅")
apply_theme()
check_login()
page_header("Appointment Management", "📅", "Schedule and track patient visits.")

tab1, tab2 = st.tabs(["Search Appointments", "Book Appointment"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        p_id = st.number_input("Patient ID", min_value=1, step=1, key="search_p")
        if st.button("Search by Patient"):
            res = api_request("GET", f"/appointments/patient/{p_id}")
            if res.status_code == 200 and res.json():
                st.dataframe(pd.DataFrame(res.json()), use_container_width=True, hide_index=True)
            else:
                st.info("No appointments found.")
    with col2:
        d_id = st.number_input("Doctor ID", min_value=1, step=1, key="search_d")
        if st.button("Search by Doctor"):
            res = api_request("GET", f"/appointments/doctor/{d_id}")
            if res.status_code == 200 and res.json():
                st.dataframe(pd.DataFrame(res.json()), use_container_width=True, hide_index=True)
            else:
                st.info("No appointments found.")

with tab2:
    with st.form("book_appt"):
        st.subheader("Schedule New Visit")
        p_id = st.number_input("Patient ID", min_value=1, step=1)
        d_id = st.number_input("Doctor ID", min_value=1, step=1)
        h_id = st.number_input("Hospital ID", min_value=1, step=1)
        appt_date = st.date_input("Date", min_value=date.today())
        appt_time = st.time_input("Time")
        reason = st.text_area("Reason")
        
        if st.form_submit_button("Book"):
            payload = {
                "patient_id": p_id, "doctor_id": d_id, "hospital_id": h_id,
                "appointment_date": str(appt_date), "time_slot": str(appt_time),
                "reason": reason, "is_follow_up": False, "status": "Scheduled"
            }
            res = api_request("POST", "/appointments", json=payload)
            if res.status_code == 201:
                st.success(f"✅ Booked! ID: {res.json()['appointment_id']}")
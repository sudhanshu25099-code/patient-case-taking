import streamlit as st
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, page_header, check_login

st.set_page_config(page_title="Clinical Dashboard", page_icon="🩺")
apply_theme()
check_login()
page_header("Clinical Dashboard", "🩺", "Pre-visit snapshots and clinical notes.")

appt_id = st.number_input("Enter Appointment ID", min_value=1, step=1)

if st.button("Load Pre-Visit Snapshot", type="primary"):
    res = api_request("GET", f"/previsit/appointment/{appt_id}")
    if res.status_code == 200:
        data = res.json()
        
        st.success(f"**Patient:** {data['patient_name']} | **Date:** {data['appointment_date']} | **Reason:** {data['reason']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Symptoms:**\n{data['todays_symptoms'] or 'None'}")
            st.error(f"**Allergies:**\n{data['active_allergies'] or 'None'}")
        with col2:
            st.warning(f"**Conditions:**\n{data['active_conditions'] or 'None'}")
            st.success(f"**Meds:**\n{data['ongoing_medicines'] or 'None'}")
            
        st.text_area("Latest Summary", value=data['latest_summary'] or "N/A", height=200, disabled=True)
    elif res.status_code == 404:
        st.warning("No appointment found.")
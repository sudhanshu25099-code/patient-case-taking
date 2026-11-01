import streamlit as st
from datetime import datetime
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, page_header, check_login

st.set_page_config(page_title="Consent", page_icon="🔏")
apply_theme()
check_login()
page_header("Consent Management", "🔏", "Grant and verify patient record access.")

tab1, tab2 = st.tabs(["Check Access", "Grant Access"])

with tab1:
    col1, col2 = st.columns(2)
    pid = col1.number_input("Patient ID", min_value=1, step=1)
    did = col2.number_input("Doctor ID", min_value=1, step=1)
    
    if st.button("Verify Consent"):
        res = api_request("GET", f"/consent/check?patient_id={pid}&doctor_id={did}")
        if res.status_code == 200:
            st.success("✅ Active consent found! Access granted.")
        else:
            st.error("❌ No active consent. Access denied.")

with tab2:
    with st.form("grant_consent"):
        p_id = st.number_input("Patient ID", min_value=1, step=1)
        h_id = st.number_input("Hospital ID", min_value=1, step=1)
        purpose = st.text_input("Purpose (e.g., Second Opinion)")
        
        if st.form_submit_button("Grant Consent"):
            payload = {
                "patient_id": p_id, "hospital_id": h_id, "consent_type": "View Only",
                "valid_from": str(datetime.now()), "status": "Active", "purpose": purpose
            }
            res = api_request("POST", "/consent", json=payload)
            if res.status_code == 201:
                st.success("✅ Consent granted!")
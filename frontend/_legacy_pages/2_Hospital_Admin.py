import streamlit as st
import pandas as pd
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, page_header, check_login

st.set_page_config(page_title="Hospitals", page_icon="🏥")
apply_theme()
check_login()
page_header("Hospital Administration", "🏥", "Manage hospitals, departments, and doctor affiliations.")

tab1, tab2 = st.tabs(["View Hospitals", "Add Hospital"])

with tab1:
    if st.button("Refresh List"):
        res = api_request("GET", "/hospitals")
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    with st.form("add_hospital"):
        name = st.text_input("Hospital Name")
        reg_no = st.text_input("Registration No")
        city = st.text_input("City")
        email = st.text_input("Email")
        
        if st.form_submit_button("Add Hospital"):
            payload = {"name": name, "registration_no": reg_no, "city": city, "email": email}
            res = api_request("POST", "/hospitals", json=payload)
            if res.status_code == 201:
                st.success(f"✅ Hospital added! ID: {res.json()['hospital_id']}")
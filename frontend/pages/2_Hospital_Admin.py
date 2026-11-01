"""
Hospital & Facility Administration
Manages Hospitals, Clinical Departments, Doctor-Hospital Affiliations, and Facilities Capacity.
"""

import streamlit as st
import pandas as pd
from datetime import date

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge

st.set_page_config(page_title="Hospital Admin • HealthPulse", page_icon="🏛️", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="Hospital & Facilities Administration",
    subtitle="Healthcare Facility Registry, Clinical Department Config, and Physician Affiliations",
    badge_text="Module 2",
    icon="🏛️"
)

tabs = st.tabs(["🏥 Hospitals & Facilities", "🏢 Departments", "🔗 Doctor Affiliations", "📊 Facility Analytics"])

# ------------------------------------------------------------------------------
# TAB 1: HOSPITALS
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 🏥 Registered Hospitals & Clinics")
    hospitals = client.list_hospitals()

    col_hosp_list, col_hosp_form = st.columns([1.6, 1.2])

    with col_hosp_list:
        for h in hospitals:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.25rem; margin-bottom: 0.85rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.2rem; font-weight: 700; color: #0284c7;">{h.get('name')}</div>
                    <span class="badge badge-active">{h.get('registration_no')}</span>
                </div>
                <div style="font-size: 0.875rem; color: #334155; margin-top: 0.4rem;">
                    📍 {h.get('address')}, {h.get('city')}, {h.get('state')}
                </div>
                <div style="font-size: 0.825rem; color: #64748b; margin-top: 0.25rem;">
                    📞 <strong>Phone:</strong> {h.get('contact_no')} | ✉️ <strong>Email:</strong> {h.get('email')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_hosp_form:
        with st.expander("➕ Register New Hospital Facility", expanded=True):
            with st.form("new_hospital_form"):
                h_name = st.text_input("Hospital Name", placeholder="e.g. St. Jude Trauma & Research Hospital")
                reg_no = st.text_input("Registration / License No.", placeholder="e.g. REG-DEL-2026-102")
                address = st.text_input("Street Address", placeholder="e.g. 88 Outer Ring Road")
                c1, c2 = st.columns(2)
                with c1:
                    city = st.text_input("City", value="New Delhi")
                with c2:
                    state = st.text_input("State", value="Delhi")
                c3, c4 = st.columns(2)
                with c3:
                    contact = st.text_input("Helpline Phone", placeholder="011-2345678")
                with c4:
                    email = st.text_input("Official Email", placeholder="info@hospital.org")

                if st.form_submit_button("Register Facility", type="primary", use_container_width=True):
                    if h_name and reg_no:
                        res = client.create_hospital({
                            "name": h_name,
                            "registration_no": reg_no,
                            "address": address,
                            "city": city,
                            "state": state,
                            "contact_no": contact,
                            "email": email
                        })
                        st.success(f"Hospital registered successfully! Facility ID: #{res.get('hospital_id')}")
                        st.rerun()
                    else:
                        st.error("Hospital Name and Registration No are required.")

# ------------------------------------------------------------------------------
# TAB 2: DEPARTMENTS
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 🏢 Clinical Departments by Facility")
    hospitals = client.list_hospitals()
    hosp_map = {h["hospital_id"]: h["name"] for h in hospitals}
    
    selected_hosp = st.selectbox(
        "Filter by Hospital",
        options=list(hosp_map.keys()),
        format_func=lambda x: hosp_map.get(x, f"Hospital #{x}")
    )

    departments = client.list_departments(hospital_id=selected_hosp)

    d_col1, d_col2 = st.columns([1.6, 1.2])

    with d_col1:
        st.markdown(f"**Found {len(departments)} Departments in {hosp_map[selected_hosp]}**")
        for dept in departments:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; margin-bottom: 0.65rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">
                    🩺 {dept.get('name')} <span style="font-size: 0.75rem; color: #64748b; font-weight: 400;">(Dept ID: #{dept.get('department_id')})</span>
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-top: 0.3rem;">
                    {dept.get('description', 'Comprehensive clinical unit')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with d_col2:
        with st.expander("➕ Add Department to Facility", expanded=True):
            with st.form("new_dept_form"):
                dept_name = st.text_input("Department Name", placeholder="e.g. Oncology, Nephrology, Dermatology")
                dept_desc = st.text_area("Scope & Description", placeholder="e.g. Chemotherapy, cancer screening, inpatient oncology ward...")
                
                if st.form_submit_button("Create Department", type="primary", use_container_width=True):
                    if dept_name:
                        client.create_department(selected_hosp, {
                            "name": dept_name,
                            "description": dept_desc
                        })
                        st.success(f"Department '{dept_name}' added to {hosp_map[selected_hosp]}!")
                        st.rerun()

# ------------------------------------------------------------------------------
# TAB 3: DOCTOR AFFILIATIONS
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🔗 Doctor-Hospital Affiliations & OPD Roster")
    doctors = client.list_doctors()
    
    aff_col1, aff_col2 = st.columns([1.6, 1.2])

    with aff_col1:
        st.markdown("#### Active Physician Roster")
        doc_rows = []
        for d in doctors:
            h_name = hosp_map.get(d.get("hospital_id", 1), "Apex Heart Hospital")
            doc_rows.append({
                "Doctor ID": f"#{d['doctor_id']}",
                "Doctor Name": d["full_name"],
                "Specialization": d["specialization"],
                "Facility": h_name,
                "Consultation Fee": f"₹{d.get('consultation_fee', 0)}"
            })
        st.dataframe(pd.DataFrame(doc_rows), use_container_width=True, hide_index=True)

    with aff_col2:
        with st.expander("➕ Affiliate Doctor to Hospital", expanded=True):
            with st.form("affiliate_form"):
                doc_opts = {d["doctor_id"]: f"{d['full_name']} ({d['specialization']})" for d in doctors}
                target_doc = st.selectbox("Select Doctor", options=list(doc_opts.keys()), format_func=lambda x: doc_opts.get(x))
                target_hosp = st.selectbox("Select Hospital Facility", options=list(hosp_map.keys()), format_func=lambda x: hosp_map.get(x))
                
                # Fetch departments for that hospital
                dept_opts = {dp["department_id"]: dp["name"] for dp in client.list_departments(target_hosp)}
                target_dept = st.selectbox("Department", options=list(dept_opts.keys()), format_func=lambda x: dept_opts.get(x))
                
                join_date = st.date_input("Joined Date", value=date.today())
                is_active = st.checkbox("Active OPD Practicing Status", value=True)

                if st.form_submit_button("Save Affiliation", type="primary", use_container_width=True):
                    # Update local state
                    for doc in client.mock_db["doctors"]:
                        if doc["doctor_id"] == target_doc:
                            doc["hospital_id"] = target_hosp
                            doc["department_id"] = target_dept
                    st.success("Doctor affiliated successfully!")
                    st.rerun()

# ------------------------------------------------------------------------------
# TAB 4: FACILITY ANALYTICS
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 📊 Facilities & Clinical Capacity Analytics")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Operational Hospitals", len(hospitals))
    with c2:
        st.metric("Total Clinical Departments", len(client.mock_db["departments"]))
    with c3:
        st.metric("Total Affiliated Physicians", len(doctors))

    st.markdown("#### Department Distribution Across Facilities")
    dept_df = pd.DataFrame(client.mock_db["departments"])
    dept_summary = dept_df.groupby("hospital_id").count()[["name"]].rename(columns={"name": "Departments Count"}).reset_index()
    dept_summary["Hospital Name"] = dept_summary["hospital_id"].map(hosp_map)
    st.bar_chart(dept_summary.set_index("Hospital Name")["Departments Count"])

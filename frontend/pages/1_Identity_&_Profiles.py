"""
Identity & Profiles Management
Handles Patients, Doctors, Nurses, Person Master Directory, User Accounts & Role Assignments.
"""

import streamlit as st
import pandas as pd
from datetime import date

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge

st.set_page_config(page_title="Identity & Profiles • HealthPulse", page_icon="👤", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="Identity & Profile Governance",
    subtitle="Master Person Directory, Clinical Staff Credentials, Patient Profiles & Role-Based Access Control",
    badge_text="Module 1",
    icon="👤"
)

tabs = st.tabs(["👥 Patients", "👨‍⚕️ Doctors", "👩‍⚕️ Nurses", "📋 Person Master & Accounts"])

# ------------------------------------------------------------------------------
# TAB 1: PATIENTS
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 👥 Patient Registry")
    
    patients = client.list_patients()
    search_query = st.text_input("🔍 Search Patients by Name or Blood Group", placeholder="Type name (e.g. Aarav, Simran) or Blood Group (e.g. B+, O+)...")
    
    filtered_patients = patients
    if search_query:
        q = search_query.lower()
        filtered_patients = [
            p for p in patients
            if q in p.get("full_name", "").lower() or q in str(p.get("blood_group", "")).lower()
        ]

    col_list, col_form = st.columns([1.6, 1.2])

    with col_list:
        st.markdown(f"**Showing {len(filtered_patients)} Patients**")
        for p in filtered_patients:
            with st.container():
                st.markdown(f"""
                <div class="glass-card" style="padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">{p.get('full_name')}</span>
                        <span style="background: #e0f2fe; color: #0369a1; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
                            Blood: {p.get('blood_group', 'N/A')}
                        </span>
                    </div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 0.4rem;">
                        <strong>Patient ID:</strong> #{p.get('patient_id')} | <strong>ABHA Linked:</strong> {'✅ Yes' if p.get('abha_linked') else '❌ No'}
                    </div>
                    <div style="font-size: 0.825rem; color: #64748b; margin-top: 0.25rem;">
                        <strong>Emergency Contact:</strong> {p.get('emergency_contact_name', 'None')} ({p.get('emergency_contact_phone', 'None')})
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_form:
        with st.expander("➕ Register New Patient Profile", expanded=True):
            with st.form("new_patient_form"):
                st.markdown("##### 1. Select or Create Person")
                persons = client.list_persons()
                person_opts = {p["person_id"]: f"{p['full_name']} ({p.get('city','')} - {p.get('phone','')})" for p in persons}
                selected_pid = st.selectbox("Associated Person", options=list(person_opts.keys()), format_func=lambda x: person_opts.get(x, f"Person #{x}"))
                
                st.markdown("##### 2. Clinical Profile Data")
                blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                em_name = st.text_input("Emergency Contact Full Name", placeholder="e.g. Ramesh Mehta")
                em_phone = st.text_input("Emergency Contact Phone", placeholder="e.g. 9810000099")
                abha_linked = st.checkbox("Link Ayushman Bharat Health Account (ABHA)", value=True)

                submitted = st.form_submit_button("Register Patient Profile", type="primary", use_container_width=True)
                if submitted:
                    new_patient_data = {
                        "person_id": selected_pid,
                        "blood_group": blood_group,
                        "emergency_contact_name": em_name,
                        "emergency_contact_phone": em_phone,
                        "abha_linked": abha_linked
                    }
                    res = client.create_patient(new_patient_data)
                    st.success(f"Patient profile created successfully! Patient ID: #{res.get('patient_id')}")
                    st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: DOCTORS
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 👨‍⚕️ Medical Specialists Directory")
    doctors = client.list_doctors()

    d_col1, d_col2 = st.columns([1.6, 1.2])

    with d_col1:
        for d in doctors:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.15rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #0369a1;">{d.get('full_name')}</div>
                    <span class="badge badge-active">{d.get('specialization', 'General')}</span>
                </div>
                <div style="font-size: 0.85rem; color: #334155; margin-top: 0.35rem;">
                    <strong>Qualifications:</strong> {d.get('qualification', 'MBBS')} | <strong>License:</strong> <code>{d.get('license_no')}</code>
                </div>
                <div style="font-size: 0.825rem; color: #64748b; margin-top: 0.25rem;">
                    <strong>Experience:</strong> {d.get('experience_years', 0)} Years | <strong>OPD Fee:</strong> ₹{d.get('consultation_fee', 0)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with d_col2:
        with st.expander("➕ Onboard New Doctor", expanded=True):
            with st.form("new_doctor_form"):
                persons = client.list_persons()
                person_opts = {p["person_id"]: f"{p['full_name']} ({p.get('phone','')})" for p in persons}
                doc_pid = st.selectbox("Person Record", options=list(person_opts.keys()), format_func=lambda x: person_opts.get(x, f"Person #{x}"))
                license_no = st.text_input("Medical License No.", placeholder="e.g. MCI-DL-2024-5501")
                specialization = st.selectbox("Specialization", ["Cardiology", "General Medicine", "Orthopedics", "Pulmonology", "Pediatrics", "Neurology", "Endocrinology", "Radiology"])
                qualification = st.text_input("Qualifications", value="MBBS, MD")
                experience = st.number_input("Experience (Years)", min_value=0, max_value=60, value=10)
                fee = st.number_input("Consultation Fee (₹)", min_value=100.0, max_value=10000.0, value=1000.0, step=100.0)

                doc_submit = st.form_submit_button("Register Doctor Profile", type="primary", use_container_width=True)
                if doc_submit:
                    doc_data = {
                        "person_id": doc_pid,
                        "license_no": license_no,
                        "specialization": specialization,
                        "qualification": qualification,
                        "experience_years": experience,
                        "consultation_fee": fee
                    }
                    res = client.create_doctor(doc_data)
                    st.success(f"Doctor profile created! Doctor ID: #{res.get('doctor_id')}")
                    st.rerun()

# ------------------------------------------------------------------------------
# TAB 3: NURSES
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 👩‍⚕️ Nursing & Ward Operations")
    nurses = client.list_nurses()

    n_col1, n_col2 = st.columns([1.6, 1.2])

    with n_col1:
        for n in nurses:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{n.get('full_name')}</span>
                    <span class="badge badge-scheduled">Shift: {n.get('shift', 'Morning')}</span>
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-top: 0.35rem;">
                    <strong>Employee ID:</strong> <code>{n.get('employee_no')}</code> | <strong>Department ID:</strong> #{n.get('department_id', 1)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with n_col2:
        with st.expander("➕ Onboard Nursing Staff", expanded=True):
            with st.form("new_nurse_form"):
                persons = client.list_persons()
                person_opts = {p["person_id"]: p["full_name"] for p in persons}
                nurse_pid = st.selectbox("Person Record", options=list(person_opts.keys()), format_func=lambda x: person_opts.get(x, f"Person #{x}"))
                emp_no = st.text_input("Employee No.", placeholder="e.g. EMP-NR-105")
                shift = st.selectbox("Shift Assignment", ["Morning", "Evening", "Night"])

                if st.form_submit_button("Register Nurse Profile", type="primary", use_container_width=True):
                    res = client.create_nurse({
                        "person_id": nurse_pid,
                        "employee_no": emp_no,
                        "shift": shift,
                        "department_id": 1
                    })
                    st.success(f"Nurse registered! ID: #{res.get('nurse_id')}")
                    st.rerun()

# ------------------------------------------------------------------------------
# TAB 4: PERSON MASTER & USER ACCOUNTS
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 📋 Master Person Directory & Accounts")
    
    col_master, col_acc = st.columns([1.5, 1.3])

    with col_master:
        st.markdown("#### Persons Directory")
        persons = client.list_persons()
        df_persons = pd.DataFrame(persons)[["person_id", "full_name", "gender", "phone", "email", "city", "state"]]
        st.dataframe(df_persons, use_container_width=True, hide_index=True)

        with st.expander("➕ Add New Person to Master Directory"):
            with st.form("create_person_form"):
                fn = st.text_input("Full Name", placeholder="e.g. Priya Sundaram")
                c1, c2 = st.columns(2)
                with c1:
                    dob = st.date_input("Date of Birth", value=date(1990, 1, 1))
                    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                with c2:
                    ph = st.text_input("Phone Number", placeholder="e.g. 9810000020")
                    em = st.text_input("Email", placeholder="e.g. priya@example.com")
                addr = st.text_input("Residential Address", placeholder="e.g. Flat 402, Green Valley")
                c3, c4 = st.columns(2)
                with c3:
                    city = st.text_input("City", value="New Delhi")
                with c4:
                    state = st.text_input("State", value="Delhi")

                if st.form_submit_button("Save Person to Master DB", type="primary", use_container_width=True):
                    new_p = client.create_person({
                        "full_name": fn,
                        "date_of_birth": str(dob),
                        "gender": gender,
                        "phone": ph,
                        "email": em,
                        "address": addr,
                        "city": city,
                        "state": state
                    })
                    st.success(f"Person created! Person ID: #{new_p.get('person_id')}")
                    st.rerun()

    with col_acc:
        st.markdown("#### User Accounts & Role Permissions")
        users = client.mock_db.get("users", [])
        roles = client.list_roles()
        role_map = {r["role_id"]: r["role_name"] for r in roles}

        df_users = pd.DataFrame(users)[["user_id", "username", "email", "is_active", "last_login"]]
        st.dataframe(df_users, use_container_width=True, hide_index=True)

        with st.expander("🛡️ Assign System Role to User"):
            user_opts = {u["user_id"]: f"{u['username']} (ID: #{u['user_id']})" for u in users}
            target_user = st.selectbox("Select User Account", options=list(user_opts.keys()), format_func=lambda x: user_opts.get(x))
            target_role = st.selectbox("Assign Role", options=list(role_map.keys()), format_func=lambda x: role_map.get(x))

            if st.button("Authorize & Assign Role", use_container_width=True):
                client.assign_role(target_user, target_role)
                st.success(f"Role '{role_map[target_role]}' assigned to User #{target_user}!")

        with st.expander("🔑 Reset / Update Password"):
            pwd_user = st.selectbox("Account to Update", options=list(user_opts.keys()), format_func=lambda x: user_opts.get(x), key="pwd_user")
            new_pwd = st.text_input("New Secure Password", type="password")
            if st.button("Change Password", use_container_width=True):
                if new_pwd.strip():
                    client.change_password(pwd_user, new_pwd)
                    st.success(f"Password updated for {user_opts[pwd_user]}!")
                else:
                    st.warning("Password cannot be blank.")

import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.api_client import api_request, fetch_json
from utils.ui_helpers import page_header, render_kpi_card, render_status_badge, check_login
from utils.ai_engine import generate_mock_summary


def admin_overview_view():
    check_login()
    page_header("Executive Command Center", "📊", "Enterprise Healthcare Network Overview • FastAPI + MySQL")

    patients = fetch_json("/identity/patients", [])
    doctors = fetch_json("/identity/doctors", [])
    nurses = fetch_json("/identity/nurses", [])
    hospitals = fetch_json("/hospitals", [])
    appointments = fetch_json("/appointments", [])
    tests = fetch_json("/diagnostics/tests", [])

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_kpi_card("Patients", len(patients), "Registered in EHR", "👥")
    with c2:
        render_kpi_card("Doctors", len(doctors), "Consulting Staff", "👨‍⚕️")
    with c3:
        render_kpi_card("Nurses", len(nurses), "Nursing Station", "👩‍⚕️")
    with c4:
        render_kpi_card("Hospitals", len(hospitals), "Network Facilities", "🏥")
    with c5:
        render_kpi_card("Appointments", len(appointments), "Scheduled & Active", "📅")
    with c6:
        render_kpi_card("Lab Catalog", len(tests), "Standard Panels", "🧪")

    st.markdown("---")
    st.subheader("🏥 Network Facilities")
    if hospitals:
        st.dataframe(pd.DataFrame(hospitals), use_container_width=True, hide_index=True)

    st.subheader("📅 Recent Appointments")
    if appointments:
        st.dataframe(pd.DataFrame(appointments).head(10), use_container_width=True, hide_index=True)


def admin_hospitals_view():
    check_login()
    page_header("Hospital & Facility Administration", "🏥", "Manage network hospitals, clinical departments, and doctor affiliations")

    tab_view, tab_add_hosp, tab_add_dept, tab_link_doc = st.tabs([
        "🏢 Hospital Facilities", "➕ Add Hospital", "🏬 Add Department", "🔗 Doctor Affiliations"
    ])

    with tab_view:
        hospitals = fetch_json("/hospitals", [])
        if hospitals:
            st.dataframe(pd.DataFrame(hospitals), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("Departments per Hospital")
            h_map = {h["name"]: h["hospital_id"] for h in hospitals}
            sel_h = st.selectbox("Select Hospital to view departments", list(h_map.keys()))
            depts = fetch_json(f"/hospitals/{h_map[sel_h]}/departments", [])
            if depts:
                st.dataframe(pd.DataFrame(depts), use_container_width=True, hide_index=True)
            else:
                st.info("No departments registered for this hospital yet.")

    with tab_add_hosp:
        with st.form("add_hospital_form"):
            st.subheader("Register New Healthcare Facility")
            name = st.text_input("Hospital Name", placeholder="e.g. Apex Multispeciality Hospital")
            c_reg, c_city = st.columns(2)
            reg_no = c_reg.text_input("Registration / License No", placeholder="e.g. HOSP-DEL-2026-09")
            city = c_city.text_input("City", placeholder="New Delhi")

            c_addr, c_state = st.columns(2)
            address = c_addr.text_input("Address", placeholder="Plot 45, Institutional Area")
            state = c_state.text_input("State", placeholder="Delhi")

            c_phone, c_email = st.columns(2)
            contact_no = c_phone.text_input("Contact No", placeholder="011-29801234")
            email = c_email.text_input("Official Email", placeholder="admin@apexhospital.org")

            if st.form_submit_button("Register Hospital", type="primary"):
                payload = {
                    "name": name, "registration_no": reg_no, "address": address,
                    "city": city, "state": state, "contact_no": contact_no, "email": email
                }
                res = api_request("POST", "/hospitals", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ Hospital registered! ID: #{res.json().get('hospital_id')}")
                    st.rerun()
                else:
                    st.error("Failed to register hospital.")

    with tab_add_dept:
        hospitals = fetch_json("/hospitals", [])
        if hospitals:
            h_map = {h["name"]: h["hospital_id"] for h in hospitals}
            with st.form("add_dept_form"):
                st.subheader("Add Department")
                sel_h = st.selectbox("Hospital", list(h_map.keys()))
                dept_name = st.text_input("Department Name", placeholder="e.g. Cardiology, Neurology, Orthopedics")
                desc = st.text_input("Description", placeholder="Inpatient and outpatient cardiac care")

                if st.form_submit_button("Create Department", type="primary"):
                    payload = {"name": dept_name, "description": desc}
                    res = api_request("POST", f"/hospitals/{h_map[sel_h]}/departments", json=payload)
                    if res and res.status_code == 201:
                        st.success(f"✅ Department created! ID: #{res.json().get('department_id')}")
                    else:
                        st.error("Failed to create department.")

    with tab_link_doc:
        hospitals = fetch_json("/hospitals", [])
        doctors = fetch_json("/identity/doctors", [])
        if hospitals and doctors:
            h_map = {h["name"]: h["hospital_id"] for h in hospitals}
            d_map = {f"Dr. {d['full_name']} ({d.get('specialization', 'Physician')})": d["doctor_id"] for d in doctors}

            with st.form("link_doc_form"):
                st.subheader("Affiliate Doctor to Hospital")
                sel_h = st.selectbox("Select Hospital", list(h_map.keys()))
                sel_d = st.selectbox("Select Doctor", list(d_map.keys()))

                if st.form_submit_button("Affiliate Doctor", type="primary"):
                    payload = {
                        "doctor_id": d_map[sel_d],
                        "hospital_id": h_map[sel_h],
                        "joined_date": str(date.today()),
                        "is_active": True
                    }
                    res = api_request("POST", f"/hospitals/{h_map[sel_h]}/doctors/{d_map[sel_d]}", json=payload)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ Doctor affiliation recorded!")
                    else:
                        st.error("Could not link doctor.")


def admin_users_view():
    check_login()
    page_header("User & Identity Management", "👥", "Manage persons, user accounts, role assignments, and clinical staff profiles")

    tab_users, tab_person, tab_user, tab_role, tab_prof = st.tabs([
        "📋 User Directory", "➕ Register Person", "🔑 Create User Account", "🛡️ Assign Role", "🏥 Create Staff Profile"
    ])

    with tab_users:
        users = fetch_json("/identity/users", [])
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
        else:
            st.info("No user accounts found.")

    with tab_person:
        with st.form("create_person_form"):
            st.subheader("Register New Person")
            full_name = st.text_input("Full Name", placeholder="e.g. Ramesh Chandra")
            c_dob, c_gen = st.columns(2)
            dob = c_dob.date_input("Date of Birth", value=date(1985, 1, 1))
            gender = c_gen.selectbox("Gender", ["Male", "Female", "Other"])

            c_phone, c_email = st.columns(2)
            phone = c_phone.text_input("Phone Number", placeholder="9810000000")
            email = c_email.text_input("Email", placeholder="user@example.com")

            c_addr, c_city, c_state = st.columns(3)
            addr = c_addr.text_input("Address", placeholder="12 Green Park")
            city = c_city.text_input("City", placeholder="New Delhi")
            state = c_state.text_input("State", placeholder="Delhi")

            if st.form_submit_button("Register Person", type="primary"):
                payload = {
                    "full_name": full_name, "date_of_birth": str(dob), "gender": gender,
                    "phone": phone, "email": email, "address": addr, "city": city, "state": state
                }
                res = api_request("POST", "/identity/persons", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ Person created with ID: #{res.json().get('person_id')}")
                    st.rerun()
                else:
                    st.error("Failed to create person.")

    with tab_user:
        persons = fetch_json("/identity/persons", [])
        p_map = {f"{p['full_name']} (ID: {p['person_id']})": p["person_id"] for p in persons} if persons else {}

        with st.form("create_user_account_form"):
            st.subheader("Create Login Credentials for Person")
            sel_p = st.selectbox("Select Person", list(p_map.keys()))
            username = st.text_input("Username", placeholder="e.g. dr.ramesh")
            email = st.text_input("Email", placeholder="ramesh@example.com")
            password = st.text_input("Initial Password", type="password", placeholder="Minimum 6 characters")

            if st.form_submit_button("Create User Account", type="primary"):
                payload = {
                    "person_id": p_map[sel_p],
                    "username": username,
                    "email": email,
                    "password": password,
                    "is_active": True
                }
                res = api_request("POST", "/identity/users", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ User account created! User ID: #{res.json().get('user_id')}")
                    st.rerun()
                else:
                    st.error(f"Failed to create user: {res.text if res else 'Unknown error'}")

    with tab_role:
        users = fetch_json("/identity/users", [])
        roles = fetch_json("/identity/roles", [])
        u_map = {f"{u['username']} ({u['full_name']})": u["user_id"] for u in users} if users else {}
        r_map = {r["role_name"]: r["role_id"] for r in roles} if roles else {}

        with st.form("assign_role_form"):
            st.subheader("Assign System Role")
            sel_u = st.selectbox("Select User", list(u_map.keys()))
            sel_r = st.selectbox("Select Role to Assign", list(r_map.keys()))

            if st.form_submit_button("Assign Role", type="primary"):
                payload = {"role_id": r_map[sel_r]}
                res = api_request("POST", f"/identity/users/{u_map[sel_u]}/roles", json=payload)
                if res and res.status_code in [200, 201]:
                    st.success(f"✅ Role '{sel_r}' successfully assigned!")
                    st.rerun()
                else:
                    st.error("Failed to assign role.")

    with tab_prof:
        st.subheader("Create Doctor, Nurse or Patient Clinical Profile")
        persons = fetch_json("/identity/persons", [])
        p_map = {f"{p['full_name']} (ID: {p['person_id']})": p["person_id"] for p in persons} if persons else {}

        profile_type = st.radio("Profile Type", ["Doctor Profile", "Nurse Profile", "Patient Profile"], horizontal=True)

        if profile_type == "Doctor Profile":
            with st.form("create_doc_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys()))
                lic = st.text_input("License No", placeholder="DMC-99881")
                spec = st.text_input("Specialization", placeholder="Cardiology")
                qual = st.text_input("Qualification", placeholder="MBBS, MD (Cardiology)")
                fee = st.number_input("Consultation Fee (INR)", min_value=0, value=700)

                if st.form_submit_button("Create Doctor Profile", type="primary"):
                    payload = {
                        "person_id": p_map[sel_p], "license_no": lic, "specialization": spec,
                        "qualification": qual, "consultation_fee": fee, "experience_years": 8
                    }
                    res = api_request("POST", "/identity/doctors", json=payload)
                    if res and res.status_code == 201:
                        st.success(f"✅ Doctor profile created! Doctor ID: #{res.json().get('doctor_id')}")

        elif profile_type == "Nurse Profile":
            with st.form("create_nurse_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys()))
                emp_no = st.text_input("Employee No", placeholder="NUR-2026-01")
                shift = st.selectbox("Assigned Shift", ["Morning", "Evening", "Night"])

                if st.form_submit_button("Create Nurse Profile", type="primary"):
                    payload = {"person_id": p_map[sel_p], "employee_no": emp_no, "shift": shift}
                    res = api_request("POST", "/identity/nurses", json=payload)
                    if res and res.status_code == 201:
                        st.success(f"✅ Nurse profile created! Nurse ID: #{res.json().get('nurse_id')}")

        else:
            with st.form("create_pat_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys()))
                bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                em_name = st.text_input("Emergency Contact Name")
                em_phone = st.text_input("Emergency Contact Phone")

                if st.form_submit_button("Create Patient Profile", type="primary"):
                    payload = {
                        "person_id": p_map[sel_p], "blood_group": bg,
                        "emergency_contact_name": em_name, "emergency_contact_phone": em_phone,
                        "abha_linked": False
                    }
                    res = api_request("POST", "/identity/patients", json=payload)
                    if res and res.status_code == 201:
                        st.success(f"✅ Patient profile created! Patient ID: #{res.json().get('patient_id')}")


def admin_appointments_view():
    check_login()
    page_header("Master Appointments Management", "📅", "Central scheduling ledger across all hospital facilities and consulting physicians")

    appts = fetch_json("/appointments", [])
    if appts:
        st.dataframe(pd.DataFrame(appts), use_container_width=True, hide_index=True)
    else:
        st.info("No appointments currently on file.")


def admin_clinical_view():
    check_login()
    page_header("Clinical Records & EMR Vault", "🩺", "Network-wide clinical oversight and patient case summaries")

    patients = fetch_json("/identity/patients", [])
    if patients:
        p_map = {f"{p['full_name']} (ID: {p['patient_id']})": p["patient_id"] for p in patients}
        sel_p = st.selectbox("Select Patient to inspect clinical vault", list(p_map.keys()))
        pid = p_map[sel_p]

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Diagnosed Conditions")
            conds = fetch_json(f"/visits/patient/{pid}/conditions", [])
            st.dataframe(pd.DataFrame(conds) if conds else pd.DataFrame([{"Notice": "No conditions"}]), use_container_width=True, hide_index=True)

        with c2:
            st.subheader("Allergies")
            als = fetch_json(f"/visits/patient/{pid}/allergies", [])
            st.dataframe(pd.DataFrame(als) if als else pd.DataFrame([{"Notice": "No allergies"}]), use_container_width=True, hide_index=True)


def admin_diagnostics_view():
    check_login()
    page_header("Diagnostics & Lab Catalog Master", "🔬", "Manage diagnostic test catalog, standard reference panels, and parameters")

    tests = fetch_json("/diagnostics/tests", [])
    st.dataframe(pd.DataFrame(tests), use_container_width=True, hide_index=True)


def admin_documents_view():
    check_login()
    page_header("Document Vault & Archive", "📁", "Central management of medical documents, scans, and verified reports")

    doc_types = fetch_json("/documents/types", [])
    st.subheader("Supported Document Types")
    st.dataframe(pd.DataFrame(doc_types) if doc_types else pd.DataFrame([{"Notice": "No types"}]), use_container_width=True, hide_index=True)


def admin_consent_view():
    check_login()
    page_header("Consent & Privacy Oversight", "🔏", "Monitor compliance, consent authorizations, and health record access permissions")
    st.info("Patients maintain sovereign control over their records through the patient portal.")


def admin_audit_view():
    check_login()
    page_header("Security Audit & Access Logs", "📜", "Enterprise access ledger, audit trail, and compliance tracing")

    st.subheader("Live System Audit Stream")
    logs = fetch_json("/logs/access/user/1", [])
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
    else:
        st.info("System access logs are clean and synchronized.")


def admin_ai_assistant_view():
    check_login()
    page_header("AI Clinical Assistant", "🧠", "Clinical NLP note summarization, symptom extraction, and decision support")

    raw_text = st.text_area("Clinical Input Notes", height=180, placeholder="Paste clinical text to analyze...")
    if st.button("Generate AI Clinical Summary", type="primary"):
        if raw_text:
            st.markdown(generate_mock_summary(raw_text))


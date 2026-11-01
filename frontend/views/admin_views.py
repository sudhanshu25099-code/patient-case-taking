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
    else:
        st.info("No facilities found.")

    st.subheader("📅 Recent Appointments")
    if appointments:
        st.dataframe(pd.DataFrame(appointments).head(10), use_container_width=True, hide_index=True)


def admin_hospitals_view():
    check_login()
    page_header("Hospital & Facility Administration", "🏥", "Manage network hospitals, clinical departments, and doctor affiliations")

    tab_view, tab_add_hosp, tab_add_dept, tab_link_doc = st.tabs([
        "🏢 Hospital Facilities", "➕ Add Hospital", "🏬 Add Department", "🔗 Doctor Affiliations"
    ])

    hospitals = fetch_json("/hospitals", [])

    with tab_view:
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
        else:
            st.info("No hospitals found. Use the 'Add Hospital' tab to create one.")

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
                    detail = res.json().get("detail") if res else "Connection failed"
                    st.error(f"Failed to register hospital: {detail}")

    with tab_add_dept:
        st.subheader("Add Department to Healthcare Facility")
        if hospitals:
            h_map = {h["name"]: h["hospital_id"] for h in hospitals}
            sel_h = st.selectbox("Select Hospital", list(h_map.keys()), key="dept_sel_hosp")
            sel_hid = h_map[sel_h]
            current_depts = fetch_json(f"/hospitals/{sel_hid}/departments", [])
            if current_depts:
                dept_names = [d["name"] for d in current_depts]
                st.info(f"📋 **Existing departments in {sel_h}:** " + ", ".join([f"`{n}`" for n in dept_names]))
        else:
            sel_hid = st.number_input("Hospital ID", min_value=1, value=1)

        with st.form("add_dept_form"):
            dept_name = st.text_input("New Department Name", placeholder="e.g. Oncology, Radiology, Nephrology")
            desc = st.text_input("Description", placeholder="Inpatient and outpatient specialized care")

            if st.form_submit_button("Create Department", type="primary"):
                if not dept_name.strip():
                    st.warning("Please provide a department name.")
                else:
                    payload = {"name": dept_name.strip(), "description": desc}
                    res = api_request("POST", f"/hospitals/{sel_hid}/departments", json=payload)
                    if res and res.status_code == 201:
                        st.success(f"✅ Department created! ID: #{res.json().get('department_id')}")
                        st.rerun()
                    else:
                        detail = res.json().get("detail") if res else "Connection error"
                        st.error(f"Failed to create department: {detail}")

    with tab_link_doc:
        st.subheader("Current Doctor Affiliations Across Network")
        affiliations = fetch_json("/hospitals/affiliations/all", [])
        if affiliations:
            st.dataframe(pd.DataFrame(affiliations), use_container_width=True, hide_index=True)
            
        st.markdown("---")
        doctors = fetch_json("/identity/doctors", [])
        with st.form("link_doc_form"):
            st.subheader("Affiliate / Update Doctor Affiliation")
            if hospitals:
                h_map = {h["name"]: h["hospital_id"] for h in hospitals}
                sel_h = st.selectbox("Select Hospital", list(h_map.keys()))
                sel_hid = h_map[sel_h]
            else:
                sel_hid = st.number_input("Hospital ID", min_value=1, value=1)

            if doctors:
                d_map = {f"Dr. {d['full_name']} ({d.get('specialization', 'Physician')})": d["doctor_id"] for d in doctors}
                sel_d = st.selectbox("Select Doctor", list(d_map.keys()))
                sel_did = d_map[sel_d]
            else:
                sel_did = st.number_input("Doctor ID", min_value=1, value=1)

            if st.form_submit_button("Affiliate Doctor", type="primary"):
                payload = {
                    "doctor_id": sel_did,
                    "hospital_id": sel_hid,
                    "joined_date": str(date.today()),
                    "is_active": True
                }
                res = api_request("POST", f"/hospitals/{sel_hid}/doctors/{sel_did}", json=payload)
                if res and res.status_code in [200, 201]:
                    st.success("✅ Doctor affiliation recorded/updated successfully!")
                    st.rerun()
                else:
                    detail = res.json().get("detail") if res else "Connection error"
                    st.error(f"Could not link doctor: {detail}")


def admin_users_view():
    check_login()
    page_header("User & Identity Management", "👥", "Manage persons, user accounts, role assignments, passwords, and staff profiles")

    tab_users, tab_person, tab_user, tab_role, tab_pass, tab_prof = st.tabs([
        "📋 User Directory", "➕ Register Person", "🔑 Create User Account", "🛡️ Assign Role", "🔒 Reset Password", "🏥 Create Staff Profile"
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
            if p_map:
                sel_p = st.selectbox("Select Person", list(p_map.keys()))
                sel_pid = p_map[sel_p]
            else:
                sel_pid = st.number_input("Person ID", min_value=1, value=1)

            username = st.text_input("Username", placeholder="e.g. dr.ramesh")
            email = st.text_input("Email", placeholder="ramesh@example.com")
            password = st.text_input("Initial Password", type="password", placeholder="Minimum 6 characters")

            if st.form_submit_button("Create User Account", type="primary"):
                payload = {
                    "person_id": sel_pid,
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
            if u_map and r_map:
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
            else:
                st.info("Users or roles not available.")

    with tab_pass:
        users = fetch_json("/identity/users", [])
        u_map = {f"{u['username']} ({u['full_name']})": u["user_id"] for u in users} if users else {}
        with st.form("reset_password_form"):
            st.subheader("Reset User Password")
            if u_map:
                sel_user = st.selectbox("Select User", list(u_map.keys()))
                new_pass = st.text_input("New Password", type="password")

                if st.form_submit_button("Update Password", type="primary"):
                    uid = u_map[sel_user]
                    res_p = api_request("PATCH", f"/identity/users/{uid}/password", json={"new_password": new_pass})
                    if res_p and res_p.status_code == 200:
                        st.success("✅ Password updated successfully!")
                    else:
                        st.error("Failed to update password.")

    with tab_prof:
        st.subheader("Create Doctor, Nurse or Patient Clinical Profile")
        persons = fetch_json("/identity/persons", [])
        p_map = {f"{p['full_name']} (ID: {p['person_id']})": p["person_id"] for p in persons} if persons else {}

        profile_type = st.radio("Profile Type", ["Doctor Profile", "Nurse Profile", "Patient Profile"], horizontal=True)

        if profile_type == "Doctor Profile":
            with st.form("create_doc_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys())) if p_map else None
                lic = st.text_input("License No", placeholder="DMC-99881")
                spec = st.text_input("Specialization", placeholder="Cardiology")
                qual = st.text_input("Qualification", placeholder="MBBS, MD (Cardiology)")
                fee = st.number_input("Consultation Fee (INR)", min_value=0, value=700)

                if st.form_submit_button("Create Doctor Profile", type="primary"):
                    if sel_p:
                        payload = {
                            "person_id": p_map[sel_p], "license_no": lic, "specialization": spec,
                            "qualification": qual, "consultation_fee": fee, "experience_years": 8
                        }
                        res = api_request("POST", "/identity/doctors", json=payload)
                        if res and res.status_code == 201:
                            st.success(f"✅ Doctor profile created! Doctor ID: #{res.json().get('doctor_id')}")

        elif profile_type == "Nurse Profile":
            with st.form("create_nurse_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys())) if p_map else None
                emp_no = st.text_input("Employee No", placeholder="NUR-2026-01")
                shift = st.selectbox("Assigned Shift", ["Morning", "Evening", "Night"])

                if st.form_submit_button("Create Nurse Profile", type="primary"):
                    if sel_p:
                        payload = {"person_id": p_map[sel_p], "employee_no": emp_no, "shift": shift}
                        res = api_request("POST", "/identity/nurses", json=payload)
                        if res and res.status_code == 201:
                            st.success(f"✅ Nurse profile created! Nurse ID: #{res.json().get('nurse_id')}")

        else:
            with st.form("create_pat_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys())) if p_map else None
                bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                em_name = st.text_input("Emergency Contact Name")
                em_phone = st.text_input("Emergency Contact Phone")

                if st.form_submit_button("Create Patient Profile", type="primary"):
                    if sel_p:
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

    tab_cat, tab_add_t, tab_add_p = st.tabs(["📋 Test Catalog", "➕ Add Test", "🧪 Add Parameter"])

    with tab_cat:
        tests = fetch_json("/diagnostics/tests", [])
        st.dataframe(pd.DataFrame(tests), use_container_width=True, hide_index=True)

    with tab_add_t:
        with st.form("add_test_form"):
            st.subheader("Add Diagnostic Test to Catalog")
            t_name = st.text_input("Test Name", placeholder="e.g. Vitamin D3 (25-OH)")
            cat = st.selectbox("Category", ["Blood", "Urine", "Imaging", "Pathology", "Biochemistry", "Other"])
            desc = st.text_input("Description", placeholder="Serum 25-hydroxyvitamin D measurement")

            if st.form_submit_button("Add Test", type="primary"):
                payload = {"test_name": t_name, "category": cat, "description": desc}
                res = api_request("POST", "/diagnostics/tests", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ Diagnostic test added! Test ID: #{res.json().get('test_id')}")
                    st.rerun()

    with tab_add_p:
        tests = fetch_json("/diagnostics/tests", [])
        if tests:
            t_map = {t["test_name"]: t["test_id"] for t in tests}
            with st.form("add_param_form"):
                st.subheader("Add Test Parameter")
                sel_test = st.selectbox("Diagnostic Test", list(t_map.keys()))
                p_name = st.text_input("Parameter Name", placeholder="e.g. Hemoglobin, Total Leukocyte Count")
                unit = st.text_input("Measurement Unit", placeholder="g/dL, mg/dL, /mcL")
                ref_range = st.text_input("Reference Range", placeholder="13.8 - 17.2 g/dL")

                if st.form_submit_button("Attach Parameter", type="primary"):
                    payload = {
                        "test_id": t_map[sel_test],
                        "parameter_name": p_name,
                        "unit": unit,
                        "reference_range": ref_range
                    }
                    res = api_request("POST", "/diagnostics/parameters", json=payload)
                    if res and res.status_code == 201:
                        st.success(f"✅ Parameter added to {sel_test}!")


def admin_documents_view():
    check_login()
    page_header("Document Vault & Archive", "📁", "Central management of medical documents, categories, and tags")

    tab_types, tab_tags = st.tabs(["🏷️ Document Types", "🔖 Metadata Tags"])

    with tab_types:
        doc_types = fetch_json("/documents/types", [])
        st.subheader("Supported Document Categories")
        st.dataframe(pd.DataFrame(doc_types) if doc_types else pd.DataFrame([{"Notice": "No types"}]), use_container_width=True, hide_index=True)

        with st.form("add_doc_type_form"):
            t_name = st.text_input("New Document Category Name", placeholder="e.g. Genetic Profile, Vaccination Card")
            if st.form_submit_button("Add Category", type="primary"):
                res = api_request("POST", "/documents/types", json={"name": t_name})
                if res and res.status_code == 201:
                    st.success("✅ Category added!")
                    st.rerun()

    with tab_tags:
        tags = fetch_json("/documents/tags", [])
        st.subheader("System Document Tags")
        st.dataframe(pd.DataFrame(tags) if tags else pd.DataFrame([{"Notice": "No tags"}]), use_container_width=True, hide_index=True)

        with st.form("add_tag_form"):
            tag_name = st.text_input("New Tag", placeholder="e.g. Urgent, Second-Opinion, Confidential")
            if st.form_submit_button("Create Tag", type="primary"):
                res = api_request("POST", "/documents/tags", json={"name": tag_name})
                if res and res.status_code == 201:
                    st.success("✅ Tag created!")
                    st.rerun()


def admin_consent_view():
    check_login()
    page_header("Consent & Privacy Oversight", "🔏", "Monitor compliance, consent authorizations, and health record access permissions")
    st.info("Patients maintain sovereign control over their records through the patient portal. Active consent authorizations are logged and verified on each clinical encounter.")


def admin_audit_view():
    check_login()
    page_header("Security Audit & Access Logs", "📜", "Enterprise access ledger, audit trail, and compliance tracing")

    tab_audit, tab_access, tab_notif, tab_queries = st.tabs([
        "📜 Database Table Audit", "🔐 Access Logs", "🔔 Notifications", "⚡ Live MySQL Queries"
    ])

    with tab_audit:
        sel_table = st.selectbox("Select Table Audit Trail", ["appointment", "patient_profile", "consent_record", "medical_document", "test_order"])
        audits = fetch_json(f"/logs/audit/{sel_table}", [])
        if audits:
            st.dataframe(pd.DataFrame(audits), use_container_width=True, hide_index=True)
        else:
            st.info(f"No logged audit records for table '{sel_table}'.")

    with tab_access:
        users = fetch_json("/identity/users", [])
        if users:
            u_map = {f"{u['username']} ({u['full_name']})": u["user_id"] for u in users}
            sel_u = st.selectbox("Inspect Access Logs for User", list(u_map.keys()))
            logs = fetch_json(f"/logs/access/user/{u_map[sel_u]}", [])
            if logs:
                st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
            else:
                st.info("No recorded access logs for this user.")

    with tab_notif:
        notifs = fetch_json("/logs/notifications/1", [])
        if notifs:
            for n in notifs:
                with st.expander(f"Notification #{n.get('notification_id')} (Read: {n.get('is_read')})"):
                    st.write(n.get("message"))
                    if not n.get("is_read"):
                        if st.button("Mark as Read", key=f"notif_r_{n.get('notification_id')}"):
                            api_request("PATCH", f"/logs/notifications/{n.get('notification_id')}/read")
                            st.rerun()
        else:
            st.info("No notifications pending.")

    with tab_queries:
        st.subheader("⚡ Live MySQL Connections & Queries")
        st.caption("Active threads, connection states, and executing SQL statements from MySQL Server.")
        if st.button("🔄 Refresh Queries", key="ref_proc"):
            st.rerun()

        procs = fetch_json("/logs/db/processlist", [])
        if procs:
            st.dataframe(pd.DataFrame(procs), use_container_width=True, hide_index=True)
        else:
            st.info("No active queries currently running.")


def admin_ai_assistant_view():
    check_login()
    page_header("AI Clinical Assistant", "🧠", "Clinical NLP note summarization, symptom extraction, and decision support")

    raw_text = st.text_area("Clinical Input Notes", height=180, placeholder="Paste clinical text to analyze...")
    if st.button("Generate AI Clinical Summary", type="primary"):
        if raw_text:
            st.markdown(generate_mock_summary(raw_text))

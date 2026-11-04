import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.api_client import api_request, fetch_json, handle_action_response
from utils.ui_helpers import (
    page_header, render_kpi_card, render_wide_kpi_card, render_status_badge, check_login,
    flash_success, flash_error, flash_warning
)
from utils.ai_engine import (
    generate_mock_summary, summarize_text, get_ai_config, save_groq_api_key
)


def admin_overview_view():
    check_login()
    page_header("Executive Command Center", ":material/monitoring:", "Enterprise Healthcare Network Overview • FastAPI + MySQL")

    patients = fetch_json("/identity/patients", [])
    doctors = fetch_json("/identity/doctors", [])
    nurses = fetch_json("/identity/nurses", [])
    hospitals = fetch_json("/hospitals", [])
    appointments = fetch_json("/appointments", [])
    tests = fetch_json("/diagnostics/tests", [])

    # Compute dynamic breakdown statistics for wide angle cards
    abha_count = len([p for p in patients if p.get("abha_linked")])
    em_contacts = len([p for p in patients if p.get("emergency_contact_phone")])
    bg_types = len(set(p.get("blood_group") for p in patients if p.get("blood_group")))
    pat_details = [
        ("ABHA Linked", f"{abha_count} Active"),
        ("Emergency Info", f"{em_contacts} on file"),
        ("Blood Groups", f"{bg_types} Types"),
    ]

    specs = len(set(d.get("specialization") for d in doctors if d.get("specialization")))
    avg_fee = int(sum(d.get("consultation_fee") or 0 for d in doctors) / max(len(doctors), 1))
    avg_exp = round(sum(d.get("experience_years") or 0 for d in doctors) / max(len(doctors), 1), 1)
    doc_details = [
        ("Specialties", f"{specs} Clinical"),
        ("Avg OPD Fee", f"₹{avg_fee}"),
        ("Avg Experience", f"{avg_exp} yrs"),
    ]

    shifts = ", ".join(sorted(set(n.get("shift") for n in nurses if n.get("shift")))) or "Day Shift"
    nur_details = [
        ("Active Shifts", shifts),
        ("Triage Coverage", "100% Active"),
        ("Roster Status", "On Duty"),
    ]

    cities = ", ".join(sorted(set(h.get("city") for h in hospitals if h.get("city")))) or "NCR"
    hosp_details = [
        ("Network Cities", cities),
        ("Network Status", "Online & Active"),
        ("Affiliations", "9 Linked"),
    ]

    appts_sched = len([a for a in appointments if a.get("status") == "Scheduled"])
    appts_comp = len([a for a in appointments if a.get("status") == "Completed"])
    appts_fol = len([a for a in appointments if a.get("is_follow_up")])
    appt_details = [
        ("Scheduled", f"{appts_sched} Pending"),
        ("Completed", f"{appts_comp} Visits"),
        ("Follow-Ups", f"{appts_fol} Cases"),
    ]

    cats = ", ".join(sorted(set(t.get("category") for t in tests if t.get("category")))) or "Blood, Urine, Imaging"
    test_details = [
        ("Modalities", cats),
        ("Panels Ready", f"{len(tests)} Tests"),
        ("Catalog Status", "Verified"),
    ]

    # Row 1: Patients, Doctors, Nurses (3 Columns)
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    with row1_c1:
        render_wide_kpi_card(
            title="Patients",
            value=len(patients),
            subtitle="Registered in enterprise EHR",
            icon=":material/groups:",
            badge="Demographics",
            details=pat_details
        )
    with row1_c2:
        render_wide_kpi_card(
            title="Doctors",
            value=len(doctors),
            subtitle="Consulting medical specialists",
            icon=":material/stethoscope:",
            badge="Clinical Staff",
            details=doc_details
        )
    with row1_c3:
        render_wide_kpi_card(
            title="Nurses",
            value=len(nurses),
            subtitle="Nursing station & triage",
            icon=":material/medical_services:",
            badge="Nursing Station",
            details=nur_details
        )

    # Row 2: Hospitals, Appointments, Lab Catalog (3 Columns)
    row2_c1, row2_c2, row2_c3 = st.columns(3)
    with row2_c1:
        render_wide_kpi_card(
            title="Hospitals",
            value=len(hospitals),
            subtitle="Connected healthcare centers",
            icon=":material/local_hospital:",
            badge="Facilities",
            details=hosp_details
        )
    with row2_c2:
        render_wide_kpi_card(
            title="Appointments",
            value=len(appointments),
            subtitle="Master consultation ledger",
            icon=":material/calendar_month:",
            badge="OPD Visits",
            details=appt_details
        )
    with row2_c3:
        render_wide_kpi_card(
            title="Lab Catalog",
            value=len(tests),
            subtitle="Diagnostic panels & tests",
            icon=":material/experiment:",
            badge="Diagnostics",
            details=test_details
        )

    st.markdown("---")
    st.subheader(":material/local_hospital: Network Facilities")
    if hospitals:
        st.dataframe(pd.DataFrame(hospitals), use_container_width=True, hide_index=True)
    else:
        st.info("No facilities found.")

    st.subheader(":material/calendar_month: Recent Appointments")
    if appointments:
        st.dataframe(pd.DataFrame(appointments).head(10), use_container_width=True, hide_index=True)


def admin_hospitals_view():
    check_login()
    page_header("Hospital & Facility Administration", ":material/local_hospital:", "Manage network hospitals, clinical departments, and doctor affiliations")

    tab_view, tab_add_hosp, tab_add_dept, tab_link_doc = st.tabs([
        ":material/domain: Hospital Facilities", ":material/add_circle: Add Hospital", ":material/apartment: Add Department", ":material/link: Doctor Affiliations"
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
                if not name.strip() or not reg_no.strip():
                    flash_warning("Please provide both Hospital Name and Registration Number.")
                    st.rerun()
                payload = {
                    "name": name.strip(), "registration_no": reg_no.strip(), "address": address,
                    "city": city, "state": state, "contact_no": contact_no, "email": email
                }
                res = api_request("POST", "/hospitals", json=payload)
                hid = res.json().get('hospital_id') if res and res.status_code == 201 else ''
                handle_action_response(
                    res,
                    success_msg=f"Healthcare facility '{name}' registered successfully! (Facility ID #{hid})",
                    error_prefix="Failed to register hospital",
                    rerun=True
                )

    with tab_add_dept:
        st.subheader("Add Department to Healthcare Facility")
        if hospitals:
            h_map = {h["name"]: h["hospital_id"] for h in hospitals}
            sel_h = st.selectbox("Select Hospital", list(h_map.keys()), key="dept_sel_hosp")
            sel_hid = h_map[sel_h]
            current_depts = fetch_json(f"/hospitals/{sel_hid}/departments", [])
            if current_depts:
                dept_names = [d["name"] for d in current_depts]
                st.info(f":material/assignment: **Existing departments in {sel_h}:** " + ", ".join([f"`{n}`" for n in dept_names]))
        else:
            sel_hid = st.number_input("Hospital ID", min_value=1, value=1)
            sel_h = f"Hospital #{sel_hid}"

        with st.form("add_dept_form"):
            dept_name = st.text_input("New Department Name", placeholder="e.g. Oncology, Radiology, Nephrology")
            desc = st.text_input("Description", placeholder="Inpatient and outpatient specialized care")

            if st.form_submit_button("Create Department", type="primary"):
                if not dept_name.strip():
                    flash_warning("Please provide a department name.")
                    st.rerun()
                payload = {"name": dept_name.strip(), "description": desc}
                res = api_request("POST", f"/hospitals/{sel_hid}/departments", json=payload)
                did = res.json().get('department_id') if res and res.status_code == 201 else ''
                handle_action_response(
                    res,
                    success_msg=f"Department '{dept_name}' created successfully in {sel_h}! (Dept ID #{did})",
                    error_prefix=f"Failed to create department in {sel_h}",
                    rerun=True
                )

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
                sel_h = f"Hospital #{sel_hid}"

            if doctors:
                d_map = {f"Dr. {d['full_name']} ({d.get('specialization', 'Physician')})": d["doctor_id"] for d in doctors}
                sel_d = st.selectbox("Select Doctor", list(d_map.keys()))
                sel_did = d_map[sel_d]
            else:
                sel_did = st.number_input("Doctor ID", min_value=1, value=1)
                sel_d = f"Doctor #{sel_did}"

            if st.form_submit_button("Affiliate Doctor", type="primary"):
                payload = {
                    "doctor_id": sel_did,
                    "hospital_id": sel_hid,
                    "joined_date": str(date.today()),
                    "is_active": True
                }
                res = api_request("POST", f"/hospitals/{sel_hid}/doctors/{sel_did}", json=payload)
                handle_action_response(
                    res,
                    success_msg=f"Affiliation confirmed: {sel_d} linked with {sel_h} successfully!",
                    error_prefix="Could not update doctor affiliation",
                    rerun=True
                )


def admin_users_view():
    check_login()
    page_header("User & Identity Management", ":material/groups:", "Manage persons, user accounts, role assignments, passwords, and staff profiles")

    tab_users, tab_person, tab_user, tab_role, tab_pass, tab_prof = st.tabs([
        ":material/assignment: User Directory", ":material/add_circle: Register Person", ":material/key: Create User Account", ":material/verified_user: Assign Role", ":material/lock: Reset Password", ":material/local_hospital: Create Staff Profile"
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
                if not full_name.strip():
                    flash_warning("Please provide person's full name.")
                    st.rerun()
                payload = {
                    "full_name": full_name.strip(), "date_of_birth": str(dob), "gender": gender,
                    "phone": phone.strip(), "email": email.strip(), "address": addr, "city": city, "state": state
                }
                res = api_request("POST", "/identity/persons", json=payload)
                pid = res.json().get('person_id') if res and res.status_code == 201 else ''
                handle_action_response(
                    res,
                    success_msg=f"Person '{full_name}' registered successfully! (Person ID #{pid})",
                    error_prefix="Failed to register person",
                    rerun=True
                )

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
                sel_p = f"Person #{sel_pid}"

            username = st.text_input("Username", placeholder="e.g. dr.ramesh")
            email = st.text_input("Email", placeholder="ramesh@example.com")
            password = st.text_input("Initial Password", type="password", placeholder="Minimum 6 characters")

            if st.form_submit_button("Create User Account", type="primary"):
                if not username.strip() or not password.strip():
                    flash_warning("Username and Password are required.")
                    st.rerun()
                payload = {
                    "person_id": sel_pid,
                    "username": username.strip(),
                    "email": email.strip(),
                    "password": password.strip(),
                    "is_active": True
                }
                res = api_request("POST", "/identity/users", json=payload)
                uid = res.json().get('user_id') if res and res.status_code == 201 else ''
                handle_action_response(
                    res,
                    success_msg=f"User account '@{username}' created successfully! (User ID #{uid})",
                    error_prefix="Failed to create user account",
                    rerun=True
                )

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
                    handle_action_response(
                        res,
                        success_msg=f"Role '{sel_r}' granted to {sel_u} successfully!",
                        error_prefix="Failed to assign role",
                        rerun=True
                    )
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
                    if not new_pass.strip():
                        flash_warning("Please provide a new password.")
                        st.rerun()
                    uid = u_map[sel_user]
                    res_p = api_request("PATCH", f"/identity/users/{uid}/password", json={"new_password": new_pass.strip()})
                    handle_action_response(
                        res_p,
                        success_msg=f"Password for {sel_user} updated successfully!",
                        error_prefix="Failed to update password",
                        rerun=True
                    )

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
                    if not sel_p:
                        flash_warning("Please select a person.")
                        st.rerun()
                    payload = {
                        "person_id": p_map[sel_p], "license_no": lic, "specialization": spec,
                        "qualification": qual, "consultation_fee": fee, "experience_years": 8
                    }
                    res = api_request("POST", "/identity/doctors", json=payload)
                    did = res.json().get('doctor_id') if res and res.status_code == 201 else ''
                    handle_action_response(
                        res,
                        success_msg=f"Doctor profile created successfully for {sel_p}! (Doctor ID #{did})",
                        error_prefix="Failed to create doctor profile",
                        rerun=True
                    )

        elif profile_type == "Nurse Profile":
            with st.form("create_nurse_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys())) if p_map else None
                emp_no = st.text_input("Employee No", placeholder="NUR-2026-01")
                shift = st.selectbox("Assigned Shift", ["Morning", "Evening", "Night"])

                if st.form_submit_button("Create Nurse Profile", type="primary"):
                    if not sel_p:
                        flash_warning("Please select a person.")
                        st.rerun()
                    payload = {"person_id": p_map[sel_p], "employee_no": emp_no, "shift": shift}
                    res = api_request("POST", "/identity/nurses", json=payload)
                    nid = res.json().get('nurse_id') if res and res.status_code == 201 else ''
                    handle_action_response(
                        res,
                        success_msg=f"Nurse profile created successfully for {sel_p}! (Nurse ID #{nid})",
                        error_prefix="Failed to create nurse profile",
                        rerun=True
                    )

        else:
            with st.form("create_pat_prof"):
                sel_p = st.selectbox("Person", list(p_map.keys())) if p_map else None
                bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                em_name = st.text_input("Emergency Contact Name")
                em_phone = st.text_input("Emergency Contact Phone")

                if st.form_submit_button("Create Patient Profile", type="primary"):
                    if not sel_p:
                        flash_warning("Please select a person.")
                        st.rerun()
                    payload = {
                        "person_id": p_map[sel_p], "blood_group": bg,
                        "emergency_contact_name": em_name, "emergency_contact_phone": em_phone,
                        "abha_linked": False
                    }
                    res = api_request("POST", "/identity/patients", json=payload)
                    pid = res.json().get('patient_id') if res and res.status_code == 201 else ''
                    handle_action_response(
                        res,
                        success_msg=f"Patient profile created successfully for {sel_p}! (Patient ID #{pid})",
                        error_prefix="Failed to create patient profile",
                        rerun=True
                    )


def admin_appointments_view():
    check_login()
    page_header("Master Appointments Management", ":material/calendar_month:", "Central scheduling ledger across all hospital facilities and consulting physicians")

    appts = fetch_json("/appointments", [])
    if appts:
        st.dataframe(pd.DataFrame(appts), use_container_width=True, hide_index=True)
    else:
        st.info("No appointments currently on file.")


def admin_clinical_view():
    check_login()
    page_header("Clinical Records & EMR Vault", ":material/stethoscope:", "Network-wide clinical oversight and patient case summaries")

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
    page_header("Diagnostics & Lab Catalog Master", ":material/labs:", "Manage diagnostic test catalog, standard reference panels, and parameters")

    tab_cat, tab_add_t, tab_add_p = st.tabs([":material/assignment: Test Catalog", ":material/add_circle: Add Test", ":material/experiment: Add Parameter"])

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
                if not t_name.strip():
                    flash_warning("Please provide a test name.")
                    st.rerun()
                payload = {"test_name": t_name.strip(), "category": cat, "description": desc}
                res = api_request("POST", "/diagnostics/tests", json=payload)
                tid = res.json().get('test_id') if res and res.status_code == 201 else ''
                handle_action_response(
                    res,
                    success_msg=f"Diagnostic test '{t_name}' added to catalog! (Test ID #{tid})",
                    error_prefix="Failed to add diagnostic test",
                    rerun=True
                )

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
                    if not p_name.strip():
                        flash_warning("Please provide parameter name.")
                        st.rerun()
                    payload = {
                        "test_id": t_map[sel_test],
                        "parameter_name": p_name.strip(),
                        "unit": unit.strip(),
                        "reference_range": ref_range.strip()
                    }
                    res = api_request("POST", "/diagnostics/parameters", json=payload)
                    handle_action_response(
                        res,
                        success_msg=f"Parameter '{p_name}' successfully attached to {sel_test}!",
                        error_prefix="Failed to attach parameter",
                        rerun=True
                    )


def admin_documents_view():
    check_login()
    page_header("Document Vault & Archive", ":material/folder:", "Central management of medical documents, categories, and tags")

    tab_types, tab_tags = st.tabs([":material/label: Document Types", ":material/bookmark: Metadata Tags"])

    with tab_types:
        doc_types = fetch_json("/documents/types", [])
        st.subheader("Supported Document Categories")
        st.dataframe(pd.DataFrame(doc_types) if doc_types else pd.DataFrame([{"Notice": "No types"}]), use_container_width=True, hide_index=True)

        with st.form("add_doc_type_form"):
            t_name = st.text_input("New Document Category Name", placeholder="e.g. Genetic Profile, Vaccination Card")
            if st.form_submit_button("Add Category", type="primary"):
                if not t_name.strip():
                    flash_warning("Please enter category name.")
                    st.rerun()
                res = api_request("POST", "/documents/types", json={"name": t_name.strip()})
                handle_action_response(
                    res,
                    success_msg=f"Document category '{t_name}' added successfully!",
                    error_prefix="Failed to add document category",
                    rerun=True
                )

    with tab_tags:
        tags = fetch_json("/documents/tags", [])
        st.subheader("System Document Tags")
        st.dataframe(pd.DataFrame(tags) if tags else pd.DataFrame([{"Notice": "No tags"}]), use_container_width=True, hide_index=True)

        with st.form("add_tag_form"):
            tag_name = st.text_input("New Tag", placeholder="e.g. Urgent, Second-Opinion, Confidential")
            if st.form_submit_button("Create Tag", type="primary"):
                if not tag_name.strip():
                    flash_warning("Please enter tag name.")
                    st.rerun()
                res = api_request("POST", "/documents/tags", json={"name": tag_name.strip()})
                handle_action_response(
                    res,
                    success_msg=f"Document tag '{tag_name}' created successfully!",
                    error_prefix="Failed to create tag",
                    rerun=True
                )


def admin_consent_view():
    check_login()
    page_header("Consent & Privacy Oversight", ":material/policy:", "Monitor compliance, consent authorizations, and health record access permissions")
    st.info("Patients maintain sovereign control over their records through the patient portal. Active consent authorizations are logged and verified on each clinical encounter.")


def admin_audit_view():
    check_login()
    page_header("Security Audit & Access Logs", ":material/receipt_long:", "Enterprise access ledger, audit trail, and compliance tracing")

    # --- Audit Summary KPIs ---
    summary = fetch_json("/logs/audit-summary", {})
    stats = summary.get("stats", {})
    if stats:
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Events", stats.get("total_events", 0))
        k2.metric("Inserts", stats.get("inserts", 0), delta_color="normal")
        k3.metric("Updates", stats.get("updates", 0), delta_color="normal")
        k4.metric("Deletes", stats.get("deletes", 0), delta_color="inverse")
        k5.metric("Tables Monitored", stats.get("tables_monitored", 0))
        st.caption(f"Audit coverage from {str(stats.get('earliest_event', 'N/A'))[:16]} to {str(stats.get('latest_event', 'N/A'))[:16]}")
        st.markdown("---")

    tab_audit, tab_access, tab_notif, tab_queries = st.tabs([
        ":material/receipt_long: Database Table Audit", ":material/admin_panel_settings: Access Logs", ":material/notifications: Notifications", ":material/bolt: Live MySQL Queries"
    ])

    with tab_audit:
        triggers = fetch_json("/logs/db/triggers", [])
        trg_count = len(triggers)
        with st.expander(f":material/verified: Active Database Audit Triggers ({trg_count} Active in MySQL Engine)"):
            st.caption("All 26 triggers in `database/05_audit_triggers.sql` execute directly inside the MySQL engine to automatically capture INSERT, UPDATE, and DELETE actions into `audit_trail`.")
            if triggers:
                st.dataframe(pd.DataFrame(triggers), use_container_width=True, hide_index=True)
            else:
                st.info("No active triggers detected. Run `database/05_audit_triggers.sql` in MySQL to enable automated auditing.")

        # Get all audited tables dynamically from DB
        audited_tables = fetch_json("/logs/audit/tables", [])
        all_table_names = [t["table_name"] for t in audited_tables]
        MONITORED_TABLES = [
            "appointment", "visit", "visit_diagnosis", "prescription", "prescription_item",
            "allergy", "patient_condition", "test_order", "test_result",
            "patient_consent", "medical_document", "medical_summary", "user_account"
        ]
        # Merge: tables with records first, then all monitored tables
        display_tables = list(dict.fromkeys(all_table_names + MONITORED_TABLES))

        c_tbl, c_act, c_ref = st.columns([3, 2, 1])
        sel_table = c_tbl.selectbox("Select Table Audit Trail", display_tables,
                                     format_func=lambda t: f"{t} ({next((x['record_count'] for x in audited_tables if x['table_name']==t), 0)} events)")
        action_filter = c_act.selectbox("Filter by Action", ["All", "INSERT", "UPDATE", "DELETE"])
        with c_ref:
            st.write("")
            if st.button(":material/refresh: Refresh", key="ref_audit"):
                st.rerun()

        act_param = action_filter if action_filter != "All" else None
        url = f"/logs/audit/{sel_table}" + (f"?action_type={act_param}" if act_param else "")
        audits = fetch_json(url, [])

        if audits:
            df = pd.DataFrame(audits)
            # Format action_type with color icons
            def fmt_action(a):
                icons = {"INSERT": "?? INSERT", "UPDATE": "?? UPDATE", "DELETE": "?? DELETE"}
                return icons.get(a, a)
            if "action_type" in df.columns:
                df["action_type"] = df["action_type"].apply(fmt_action)
            # Reorder columns for readability
            col_order = [c for c in ["audit_id", "action_time", "action_type", "table_name", "record_id", "user_name", "username", "remarks", "old_value", "new_value"] if c in df.columns]
            df = df[col_order]
            st.dataframe(df, use_container_width=True, hide_index=True, height=450)
            st.caption(f"Showing {len(audits)} audit records for table `{sel_table}`.")

            # Recent activity feed
            if summary.get("recent_activity"):
                st.markdown("#### :material/history: Recent Activity (All Tables)")
                for ev in summary["recent_activity"][:8]:
                    icon = {"INSERT": ":material/add_circle:", "UPDATE": ":material/edit:", "DELETE": ":material/delete:"}.get(ev.get("action_type"), ":material/info:")
                    st.caption(f"{icon} `{ev.get('action_time', '')[:16]}` ? **{ev.get('action_type')}** on `{ev.get('table_name')}` #{ev.get('record_id')} by {ev.get('user_name') or 'System'} ? {ev.get('remarks') or ''}")
        else:
            st.info(f"No audit records yet for table `{sel_table}`. Records will appear here automatically once changes are made via the application.")
            st.markdown("> **Note:** All future INSERT, UPDATE, and DELETE operations on this table will be automatically captured by MySQL triggers ? no manual logging required.")

    with tab_access:
        c_view, c_filter = st.columns([2, 1])
        view_mode = c_view.radio("View Mode", ["By User", "All Logs (Recent)"], horizontal=True)
        with c_filter:
            if st.button(":material/refresh: Refresh", key="ref_access"):
                st.rerun()

        if view_mode == "By User":
            users = fetch_json("/identity/users", [])
            if users:
                u_map = {f"{u['username']} ({u['full_name']})": u["user_id"] for u in users}
                sel_u = st.selectbox("Inspect Access Logs for User", list(u_map.keys()))
                logs = fetch_json(f"/logs/access/user/{u_map[sel_u]}", [])
                if logs:
                    st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
                else:
                    st.info("No recorded access logs for this user.")
        else:
            all_logs = fetch_json("/logs/access/all?limit=200", [])
            if all_logs:
                df_al = pd.DataFrame(all_logs)
                col_order_al = [c for c in ["log_id", "action_time", "action_type", "user_name", "username", "patient_name", "ip_address", "remarks"] if c in df_al.columns]
                st.dataframe(df_al[col_order_al], use_container_width=True, hide_index=True, height=450)
                st.caption(f"Showing {len(all_logs)} most recent access events.")
            else:
                st.info("No access log entries recorded yet.")

    with tab_notif:
        user_info = st.session_state.get("user_info", {})
        uid = user_info.get("user_id", 1)
        notifs = fetch_json(f"/logs/notifications/{uid}", [])
        unread = [n for n in notifs if not n.get("is_read")]
        st.caption(f"{len(unread)} unread notification(s) for your account.")
        if notifs:
            for n in notifs:
                read_icon = ":material/mark_email_read:" if n.get("is_read") else ":material/notifications_active:"
                with st.expander(f"{read_icon} {n.get('title') or 'Notification'} ? {str(n.get('created_at',''))[:16]}"):
                    st.write(n.get("message"))
                    if not n.get("is_read"):
                        if st.button("Mark as Read", key=f"notif_r_{n.get('notification_id')}"):
                            res = api_request("PATCH", f"/logs/notifications/{n.get('notification_id')}/read")
                            handle_action_response(res, "Notification marked as read!", "Failed to update notification", rerun=True)
        else:
            st.info("No notifications.")

    with tab_queries:
        st.subheader(":material/bolt: Live MySQL Engine & Query Inspector")
        st.caption("Real-time execution log from performance_schema ? capture JOIN queries, execution latency, and connection states.")

        q_mode = st.radio("Query Monitor View", ["Recent Executed SQL (Live History)", "Query Pattern Analytics (Digest)", "Active Worker Threads (Processlist)"], horizontal=True)

        if q_mode == "Recent Executed SQL (Live History)":
            c_f1, c_f2, c_btn = st.columns([2, 2, 1])
            join_only = c_f1.checkbox("Only show queries with JOINs", value=False)
            limit_q = c_f2.slider("Max Queries", 10, 100, 30, step=10)
            with c_btn:
                st.write("")
                if st.button(":material/refresh: Refresh", key="ref_live_q"):
                    st.rerun()

            queries = fetch_json(f"/logs/db/queries?join_only={join_only}&limit={limit_q}", [])
            if queries:
                for q_item in queries:
                    q_text = q_item.get("query", "")
                    has_join = bool(q_item.get("has_join"))
                    badge = ":material/join: **JOIN QUERY**" if has_join else ":material/code: **SQL**"
                    lat = q_item.get("latency_ms", 0)
                    rows_sent = q_item.get("rows_sent", 0)
                    rows_exam = q_item.get("rows_examined", 0)
                    first_line = q_text.splitlines()[0][:80]

                    with st.expander(f"{badge} ? {first_line}... ({lat} ms | Sent: {rows_sent} rows | Examined: {rows_exam})"):
                        st.code(q_text, language="sql")
                        c_m1, c_m2, c_m3 = st.columns(3)
                        c_m1.metric("Execution Latency", f"{lat} ms")
                        c_m2.metric("Rows Sent", rows_sent)
                        c_m3.metric("Rows Examined", rows_exam)
            else:
                st.info("No recent queries captured yet. Perform an action in the app (e.g. view appointments or patients) and refresh.")

        elif q_mode == "Query Pattern Analytics (Digest)":
            c_d1, c_d2 = st.columns([3, 1])
            d_join = c_d1.checkbox("Filter by JOIN queries only", value=False, key="d_join")
            with c_d2:
                if st.button(":material/refresh: Refresh", key="ref_digest"):
                    st.rerun()

            digests = fetch_json(f"/logs/db/digest?join_only={d_join}&limit=50", [])
            if digests:
                df_d = pd.DataFrame(digests)
                col_d_order = [c for c in ["query_template", "exec_count", "avg_latency_ms", "max_latency_ms", "total_rows_sent", "total_rows_examined", "last_executed"] if c in df_d.columns]
                st.dataframe(df_d[col_d_order], use_container_width=True, hide_index=True, height=450)
            else:
                st.info("No query digest statistics available.")

        else:
            if st.button(":material/refresh: Refresh Connections", key="ref_proc"):
                st.rerun()
            procs = fetch_json("/logs/db/processlist", [])
            if procs:
                st.dataframe(pd.DataFrame(procs), use_container_width=True, hide_index=True)
            else:
                st.info("No active thread queries currently running.")


def admin_ai_assistant_view():
    check_login()
    page_header("AI Clinical Assistant", ":material/neurology:", "Groq-powered clinical NLP summarization, symptom extraction, and decision support")

    # ── Tabs: Summarize | Settings ──────────────────────────────────────────
    tab_summarize, tab_settings = st.tabs([
        ":material/auto_awesome: Summarize Clinical Notes",
        ":material/settings: Groq API Settings",
    ])

    # ── Tab 1: Text Summarization ───────────────────────────────────────────
    with tab_summarize:
        cfg = get_ai_config()
        if not cfg.get("groq_configured"):
            st.warning(
                ":material/warning: **Groq API key not configured.** "
                "The assistant will fall back to a basic mock engine. "
                "Go to the **Groq API Settings** tab to add your key."
            )
        else:
            st.success(
                f":material/check_circle: Groq connected — model: `{cfg.get('model')}` "
                f"| Key: `{cfg.get('api_key_preview')}`"
            )

        st.info(":material/lightbulb: Paste raw consultation notes, nurse intake logs, or SOAP notes below. "
                "The AI engine extracts key clinical insights and generates a structured report.")

        raw_text = st.text_area(
            "Clinical Input Notes",
            height=200,
            placeholder=(
                "Patient presents with progressive dry cough since 4 days, low-grade evening fever "
                "with chills, mild shortness of breath on exertion. Denies chest pain or hemoptysis. "
                "BP 128/82, SpO2 97%, HR 88 bpm. No known allergies."
            )
        )

        col_btn, col_ctx = st.columns([2, 3])
        with col_ctx:
            context = st.selectbox(
                "Note Context",
                ["clinical", "discharge", "radiology", "pathology", "nursing", "pharmacy", "general"],
                help="Gives the AI model a hint about the type of medical text."
            )

        with col_btn:
            generate_btn = st.button(
                ":material/auto_awesome: Generate AI Summary",
                type="primary",
                use_container_width=True,
                disabled=not raw_text.strip()
            )

        if generate_btn:
            if not raw_text.strip():
                st.warning("Please enter some clinical text to analyze.")
            else:
                with st.spinner("Calling Groq LLM — processing medical NLP..."):
                    analysis = summarize_text(raw_text, context=context)
                st.markdown("---")
                st.markdown("### :material/summarize: AI-Generated Clinical Summary")
                st.markdown(analysis)

    # ── Tab 2: Groq Settings ────────────────────────────────────────────────
    with tab_settings:
        st.subheader(":material/key: Groq API Key Configuration")
        st.caption(
            "Your Groq API key is stored in `backend/.env` and loaded on startup. "
            "Updating it here takes effect immediately without restarting the server."
        )

        cfg = get_ai_config()

        if cfg.get("groq_configured"):
            st.success(f":material/check_circle: **Connected** — Key: `{cfg.get('api_key_preview')}` | Model: `{cfg.get('model')}`")
        else:
            st.error(":material/error: **Not configured** — Add your Groq API key below to enable AI summaries.")

        st.markdown("---")
        with st.form("groq_key_form"):
            new_key = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_...",
                help="Get your free key at https://console.groq.com/keys"
            )
            col_save, col_link = st.columns([1, 2])
            with col_save:
                submitted = st.form_submit_button(":material/save: Save API Key", type="primary")
            with col_link:
                st.markdown(
                    "<small>🔗 <a href='https://console.groq.com/keys' target='_blank'>Get a free Groq key →</a></small>",
                    unsafe_allow_html=True
                )

            if submitted:
                if not new_key.strip():
                    st.error("API key cannot be empty.")
                else:
                    success, msg = save_groq_api_key(new_key.strip())
                    if success:
                        st.success(f":material/check_circle: {msg}")
                        st.rerun()
                    else:
                        st.error(f":material/error: {msg}")

       
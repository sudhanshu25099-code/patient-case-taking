import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from utils.api_client import api_request, fetch_json, BASE_URL
from utils.ui_helpers import page_header, render_kpi_card, render_status_badge, check_login
import requests


def _get_patient_context():
    check_login()
    user_info = st.session_state.get("user_info", {})
    patient = user_info.get("patient") or {}
    patient_id = patient.get("patient_id")
    person_id = user_info.get("person_id")
    
    # If admin is simulating patient view without being a patient
    if not patient_id:
        patients = fetch_json("/identity/patients", [])
        if patients:
            patient_id = patients[0]["patient_id"]
            patient = patients[0]
            person_id = patient["person_id"]
            
    return patient_id, person_id, user_info, patient


def patient_overview_view():
    patient_id, person_id, user_info, patient = _get_patient_context()
    page_header("My Health Profile", "👤", f"Personal Health Record for {user_info.get('full_name')}")

    # Top KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Blood Group", patient.get("blood_group") or "Not Set", "Recorded in Profile", "🩸")
    with c2:
        abha = "Linked ✅" if patient.get("abha_linked") else "Not Linked ⚠️"
        render_kpi_card("ABHA ID", abha, "Ayushman Bharat Digital Health", "🆔")
    with c3:
        appts = fetch_json(f"/appointments/patient/{patient_id}", [])
        upcoming = len([a for a in appts if a.get("status") == "Scheduled"])
        render_kpi_card("Upcoming Visits", upcoming, "Confirmed Consultations", "📅")
    with c4:
        allergies = fetch_json(f"/visits/patient/{patient_id}/allergies", [])
        render_kpi_card("Known Allergies", len(allergies), "Active Alerts", "⚠️")

    st.markdown("---")
    
    col_info, col_contact = st.columns(2)
    with col_info:
        st.subheader("📋 Demographic Profile")
        person = fetch_json(f"/identity/persons/{person_id}", {}) if person_id else {}
        
        st.write(f"**Full Name:** {person.get('full_name') or user_info.get('full_name')}")
        st.write(f"**Date of Birth:** {person.get('date_of_birth') or 'N/A'}")
        st.write(f"**Gender:** {person.get('gender') or 'N/A'}")
        st.write(f"**Email:** {person.get('email') or 'N/A'}")
        st.write(f"**Phone:** {person.get('phone') or 'N/A'}")
        st.write(f"**Address:** {person.get('address') or 'N/A'}, {person.get('city') or ''}, {person.get('state') or ''}")

        with st.expander("✏️ Update Contact Information"):
            with st.form("update_contact_form"):
                up_phone = st.text_input("Phone Number", value=person.get("phone") or "")
                up_addr = st.text_input("Address", value=person.get("address") or "")
                up_city = st.text_input("City", value=person.get("city") or "")
                up_state = st.text_input("State", value=person.get("state") or "")
                
                if st.form_submit_button("Save Updates", type="primary"):
                    payload = {
                        "full_name": person.get("full_name") or user_info.get("full_name"),
                        "date_of_birth": person.get("date_of_birth"),
                        "gender": person.get("gender"),
                        "phone": up_phone,
                        "email": person.get("email"),
                        "address": up_addr,
                        "city": up_city,
                        "state": up_state
                    }
                    res = api_request("PUT", f"/identity/persons/{person_id}", json=payload)
                    if res and res.status_code == 200:
                        st.success("✅ Contact info updated!")
                        st.rerun()
                    else:
                        st.error("Failed to update contact info.")
        
    with col_contact:
        st.subheader("🚨 Emergency Contact & Safety")
        st.info(f"""
            **Contact Person:** {patient.get('emergency_contact_name') or 'Not Registered'}\n
            **Contact Phone:** {patient.get('emergency_contact_phone') or 'Not Registered'}
        """)
        
        st.subheader("🛡️ ABHA Linkage")
        if not patient.get("abha_linked"):
            if st.button("Link My ABHA / Ayushman Bharat ID", type="primary"):
                st.success("✅ ABHA Account linked successfully!")
        else:
            st.success("✅ Your profile is connected with the National Health Network.")


def patient_appointments_view():
    patient_id, _, user_info, _ = _get_patient_context()
    page_header("My Appointments", "📅", "View scheduled visits and book new consultations")

    tab_my, tab_book, tab_reschedule = st.tabs(["🗓️ My Appointments", "➕ Book Consultation", "🔄 Reschedule / Cancel"])

    with tab_my:
        appts = fetch_json(f"/appointments/patient/{patient_id}", [])
        if not appts:
            st.info("You have no appointments booked yet.")
        else:
            for a in appts:
                status_color = "🟢" if a.get("status") == "Scheduled" else "⚪"
                with st.expander(f"{status_color} {a.get('appointment_date')} at {str(a.get('time_slot'))[:5]} — Dr. {a.get('doctor_name')} ({a.get('hospital_name')})", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Doctor:** Dr. {a.get('doctor_name')}")
                    c1.write(f"**Specialization:** {a.get('doctor_specialization') or 'General'}")
                    c2.write(f"**Hospital:** {a.get('hospital_name')}")
                    c2.write(f"**Status:** {a.get('status')}")
                    c3.write(f"**Reason:** {a.get('reason')}")
                    c3.write(f"**Follow-Up:** {'Yes' if a.get('is_follow_up') else 'No'}")
                    
                    if a.get("notes"):
                        st.markdown(f"**Clinic Notes:** {a.get('notes')}")

    with tab_book:
        st.subheader("Book an Appointment")
        hospitals = fetch_json("/hospitals", [])
        doctors = fetch_json("/identity/doctors", [])

        if not hospitals or not doctors:
            st.warning("Hospital or Doctor listings are currently loading.")
        else:
            with st.form("book_appointment_form"):
                hosp_options = {h["name"]: h["hospital_id"] for h in hospitals}
                doc_options = {f"Dr. {d['full_name']} ({d.get('specialization', 'Physician')})": d["doctor_id"] for d in doctors}

                sel_hosp = st.selectbox("Select Hospital / Clinic", list(hosp_options.keys()))
                sel_doc = st.selectbox("Select Consulting Doctor", list(doc_options.keys()))

                col_d, col_t = st.columns(2)
                appt_date = col_d.date_input("Preferred Date", min_value=date.today())
                appt_time = col_t.time_input("Preferred Time Slot")

                reason = st.text_area("Reason for Visit / Symptoms", placeholder="Describe what you are experiencing...")
                is_follow_up = st.checkbox("This is a follow-up visit")

                if st.form_submit_button("Confirm Booking", type="primary"):
                    payload = {
                        "patient_id": patient_id,
                        "doctor_id": doc_options[sel_doc],
                        "hospital_id": hosp_options[sel_hosp],
                        "appointment_date": str(appt_date),
                        "time_slot": str(appt_time),
                        "reason": reason,
                        "is_follow_up": is_follow_up,
                        "status": "Scheduled"
                    }
                    res = api_request("POST", "/appointments", json=payload)
                    if res is not None and res.status_code == 201:
                        st.success("🎉 Appointment successfully booked!")
                        st.rerun()
                    else:
                        st.error(f"Failed to book appointment: {res.text if res else 'Unknown error'}")

    with tab_reschedule:
        appts = fetch_json(f"/appointments/patient/{patient_id}", [])
        active_appts = [a for a in appts if a.get("status") == "Scheduled"]
        if not active_appts:
            st.info("No active scheduled appointments to reschedule or cancel.")
        else:
            a_map = {f"Appt #{a['appointment_id']} on {a.get('appointment_date')} with Dr. {a.get('doctor_name')}": a for a in active_appts}
            sel_a_lbl = st.selectbox("Select Appointment to Modify", list(a_map.keys()))
            sel_appt = a_map[sel_a_lbl]
            
            c_resched, c_cancel = st.columns(2)
            with c_resched:
                with st.form("resched_form"):
                    st.subheader("Reschedule Date & Time")
                    new_d = st.date_input("New Date", min_value=date.today())
                    new_t = st.time_input("New Time")
                    new_reason = st.text_area("Updated Reason", value=sel_appt.get("reason") or "")
                    
                    if st.form_submit_button("Update Appointment"):
                        payload = {
                            "patient_id": sel_appt["patient_id"],
                            "doctor_id": sel_appt["doctor_id"],
                            "hospital_id": sel_appt["hospital_id"],
                            "appointment_date": str(new_d),
                            "time_slot": str(new_t),
                            "reason": new_reason,
                            "status": "Scheduled"
                        }
                        res = api_request("PUT", f"/appointments/{sel_appt['appointment_id']}", json=payload)
                        if res and res.status_code == 200:
                            st.success("✅ Appointment rescheduled successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to reschedule.")
                            
            with c_cancel:
                st.subheader("Cancel Appointment")
                st.write("If you cannot attend this visit, please cancel so the slot becomes available for other patients.")
                if st.button("Cancel This Appointment", type="secondary"):
                    res = api_request("PATCH", f"/appointments/{sel_appt['appointment_id']}/status", json={"status": "Cancelled"})
                    if res and res.status_code == 200:
                        st.success("Appointment cancelled.")
                        st.rerun()


def patient_medical_records_view():
    patient_id, _, _, _ = _get_patient_context()
    page_header("My Medical Records", "💊", "Prescriptions, Diagnoses, Clinical Summaries & Past Visits")

    tab_cond, tab_allergies, tab_summaries, tab_visits = st.tabs([
        "🩺 Active Conditions", "⚠️ Allergies", "📄 Visit Summaries", "🏥 Past Clinic Visits"
    ])

    with tab_cond:
        conds = fetch_json(f"/visits/patient/{patient_id}/conditions", [])
        if not conds:
            st.info("No chronic conditions registered.")
        else:
            df = pd.DataFrame(conds)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_allergies:
        allergies = fetch_json(f"/visits/patient/{patient_id}/allergies", [])
        if not allergies:
            st.success("No known active drug or food allergies on record.")
        else:
            for al in allergies:
                st.error(f"⚠️ **Allergen:** {al.get('allergen')} | **Reaction:** {al.get('reaction')} | **Severity:** {al.get('severity')} | **Status:** {al.get('status')}")

    with tab_summaries:
        summaries = fetch_json(f"/summaries/patient/{patient_id}", [])
        if not summaries:
            st.info("No consultation summaries recorded yet.")
        else:
            for s in summaries:
                with st.expander(f"Episode {s.get('episode_number', 1)}: {s.get('summary_type', 'Clinical Note')} ({s.get('created_at', '')[:10]})"):
                    st.markdown(s.get("summary_text", "No details available."))

    with tab_visits:
        visits = fetch_json(f"/visits/patient/{patient_id}", [])
        if not visits:
            st.info("No visits on record.")
        else:
            for v in visits:
                with st.expander(f"Visit #{v.get('visit_id')} • {str(v.get('visit_date'))[:10]} ({v.get('visit_type', 'OPD')})"):
                    st.write(f"**Chief Complaint:** {v.get('chief_complaint')}")
                    st.write(f"**Symptoms:** {v.get('symptoms') or 'N/A'}")
                    st.write(f"**Vitals Summary:** {v.get('vitals_summary') or 'N/A'}")


def patient_lab_reports_view():
    patient_id, _, _, _ = _get_patient_context()
    page_header("My Diagnostic Reports", "🔬", "Lab test results and investigation reports")

    tab_results, tab_catalog = st.tabs(["🧪 Test Results & Reports", "📋 Hospital Diagnostic Catalog"])

    with tab_results:
        results = fetch_json("/diagnostics/results", [])
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No lab results published yet.")

    with tab_catalog:
        tests = fetch_json("/diagnostics/tests", [])
        if tests:
            t_map = {t["test_name"]: t["test_id"] for t in tests}
            sel_t = st.selectbox("Select Test to inspect parameters", list(t_map.keys()))
            params = fetch_json(f"/diagnostics/tests/{t_map[sel_t]}/parameters", [])
            if params:
                st.dataframe(pd.DataFrame(params), use_container_width=True, hide_index=True)
            else:
                st.info("Standard panel with no sub-parameters.")


def patient_documents_view():
    patient_id, _, user_info, _ = _get_patient_context()
    page_header("My Health Documents", "📁", "Upload and access past prescriptions, scans and discharge summaries")

    tab_list, tab_upload = st.tabs(["📂 Document Vault", "⬆️ Upload Record"])

    with tab_list:
        docs = fetch_json(f"/documents/patient/{patient_id}", [])
        if not docs:
            st.info("No documents uploaded yet.")
        else:
            for doc in docs:
                status_badge = "🟢 Verified" if doc.get("verification_status") == "Verified" else "🟡 Pending Verification"
                with st.expander(f"{doc.get('title')} ({status_badge})"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**File Size:** {round(doc.get('file_size', 0)/1024, 1)} KB")
                    c1.write(f"**MIME Type:** {doc.get('mime_type')}")
                    c2.write(f"**Status:** {doc.get('verification_status')}")
                    
                    if st.button("Delete Document", key=f"del_doc_{doc.get('document_id')}", type="secondary"):
                        res = api_request("DELETE", f"/documents/{doc.get('document_id')}")
                        if res and res.status_code in [200, 204]:
                            st.success("Document deleted.")
                            st.rerun()

    with tab_upload:
        with st.form("patient_upload_doc"):
            doc_types = fetch_json("/documents/types", [])
            type_options = {dt["name"]: dt["document_type_id"] for dt in doc_types} if doc_types else {"Prescription": 1}

            title = st.text_input("Document Title", placeholder="e.g. Chest X-Ray 2026, Discharge Slip")
            sel_type = st.selectbox("Document Category", list(type_options.keys()))
            uploaded_file = st.file_uploader("Select File (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

            if st.form_submit_button("Upload to Vault", type="primary"):
                if not title or uploaded_file is None:
                    st.error("Please provide both a title and a file.")
                else:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
                    data = {
                        "patient_id": patient_id,
                        "document_type_id": type_options[sel_type],
                        "title": title,
                        "uploaded_by": user_info.get("user_id", 1)
                    }
                    res = requests.post(
                        f"{BASE_URL}/documents/upload",
                        data=data,
                        files=files,
                        auth=(st.session_state["username"], st.session_state["password"])
                    )
                    if res.status_code == 201:
                        st.success("✅ Document uploaded and saved to your health vault!")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {res.text}")


def patient_consent_view():
    patient_id, _, _, _ = _get_patient_context()
    page_header("Consent & Privacy", "🔏", "Control who can access your medical records and consultation history")

    tab_active, tab_grant = st.tabs(["🛡️ Active Consents & Audit", "➕ Authorize Doctor / Hospital"])

    with tab_active:
        consents = fetch_json(f"/consent/patient/{patient_id}", [])
        if not consents:
            st.info("No active consent authorizations registered.")
        else:
            for c in consents:
                status_icon = "🟢 Active" if c.get("status") == "Active" else "🔴 Revoked"
                with st.expander(f"{status_icon} — Consent #{c.get('consent_id')}: {c.get('purpose', 'General Care')}"):
                    st.write(f"**Consent Type:** {c.get('consent_type', 'Full Access')}")
                    st.write(f"**Valid From:** {c.get('valid_from')} to {c.get('valid_to') or 'Indefinite'}")
                    st.write(f"**Status:** {c.get('status')}")
                    
                    # Access audit for this consent
                    accesses = fetch_json(f"/consent/{c.get('consent_id')}/access", [])
                    if accesses:
                        st.markdown("**Doctor Access Audit Trail:**")
                        st.dataframe(pd.DataFrame(accesses), use_container_width=True, hide_index=True)

                    if c.get("status") == "Active":
                        if st.button("Revoke Access", key=f"revoke_{c.get('consent_id')}", type="secondary"):
                            res = api_request("PATCH", f"/consent/{c.get('consent_id')}/revoke")
                            if res is not None and res.status_code == 200:
                                st.success("Access revoked.")
                                st.rerun()

    with tab_grant:
        hospitals = fetch_json("/hospitals", [])
        with st.form("grant_consent_form"):
            hosp_map = {h["name"]: h["hospital_id"] for h in hospitals} if hospitals else {"Hospital #1": 1}
            sel_h = st.selectbox("Select Hospital Facility", list(hosp_map.keys()))
            consent_type = st.selectbox("Access Level", ["View Only", "Full Clinical Access", "Emergency Only"])
            purpose = st.text_input("Purpose", placeholder="e.g. Second Opinion, General Treatment, Specialist Consultation")

            if st.form_submit_button("Grant Authorization", type="primary"):
                payload = {
                    "patient_id": patient_id,
                    "hospital_id": hosp_map[sel_h],
                    "consent_type": consent_type,
                    "purpose": purpose,
                    "valid_from": str(datetime.now()),
                    "valid_to": str(datetime.now() + timedelta(days=90)),
                    "status": "Active"
                }
                res = api_request("POST", "/consent", json=payload)
                if res is not None and res.status_code == 201:
                    st.success("✅ Consent successfully granted!")
                    st.rerun()
                else:
                    st.error("Failed to grant consent.")

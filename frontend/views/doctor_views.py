import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.api_client import api_request, fetch_json
from utils.ui_helpers import page_header, render_kpi_card, render_status_badge, check_login
from utils.ai_engine import generate_mock_summary


def _get_doctor_context():
    check_login()
    user_info = st.session_state.get("user_info", {})
    doctor = user_info.get("doctor") or {}
    doctor_id = doctor.get("doctor_id")
    
    # If admin simulating doctor view
    if not doctor_id:
        doctors = fetch_json("/identity/doctors", [])
        if doctors:
            doctor_id = doctors[0]["doctor_id"]
            doctor = doctors[0]
            
    return doctor_id, user_info, doctor


def doctor_station_view():
    doctor_id, user_info, doctor = _get_doctor_context()
    page_header(f"Doctor Station • Dr. {user_info.get('full_name')}", "🩺", f"Specialization: {doctor.get('specialization', 'Physician')} | License: {doctor.get('license_no', 'N/A')}")

    appts = fetch_json(f"/appointments/doctor/{doctor_id}", [])
    scheduled = [a for a in appts if a.get("status") == "Scheduled"]
    completed = [a for a in appts if a.get("status") == "Completed"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Pending Queue", len(scheduled), "Appointments Awaiting", "⏳")
    with c2:
        render_kpi_card("Completed Visits", len(completed), "Concluded Consultations", "✅")
    with c3:
        render_kpi_card("Total Bookings", len(appts), "Assigned to You", "📅")
    with c4:
        render_kpi_card("Consultation Fee", f"₹{doctor.get('consultation_fee') or 500}", "Standard OPD Rate", "💳")

    st.markdown("---")
    st.subheader("📋 Patient Consultation Queue")

    if not appts:
        st.info("No appointments currently assigned to you.")
    else:
        for a in appts:
            is_pending = a.get("status") == "Scheduled"
            with st.expander(f"{'🔵 [PENDING]' if is_pending else '🟢 [COMPLETED]'} {a.get('appointment_date')} • {a.get('patient_name')} ({a.get('reason')})", expanded=is_pending):
                c_p1, c_p2, c_p3 = st.columns(3)
                c_p1.write(f"**Patient:** {a.get('patient_name')}")
                c_p1.write(f"**Phone:** {a.get('patient_phone') or 'N/A'}")
                c_p2.write(f"**Time Slot:** {str(a.get('time_slot'))[:5]}")
                c_p2.write(f"**Hospital:** {a.get('hospital_name')}")
                c_p3.write(f"**Status:** {a.get('status')}")
                c_p3.write(f"**Follow-Up:** {'Yes' if a.get('is_follow_up') else 'No'}")
                
                st.write(f"**Chief Complaint / Reason:** {a.get('reason')}")
                
                if is_pending:
                    col_b1, col_b2 = st.columns([1, 4])
                    with col_b1:
                        if st.button("🩺 Start Case Taking", key=f"start_case_{a.get('appointment_id')}", type="primary"):
                            st.session_state["active_appointment_id"] = a.get("appointment_id")
                            st.session_state["active_patient_id"] = a.get("patient_id")
                            st.session_state["active_hospital_id"] = a.get("hospital_id")
                            st.session_state["active_patient_name"] = a.get("patient_name")
                            st.info("Loaded into Clinical Case Taking! Please open the **Clinical Case Taking** tab.")


def doctor_case_taking_view():
    doctor_id, user_info, _ = _get_doctor_context()
    page_header("Clinical Case Taking & EMR", "📋", "Pre-visit snapshot, diagnosis, prescriptions, and SOAP notes")

    active_appt_id = st.session_state.get("active_appointment_id")
    
    # Selector if not preloaded
    appts = fetch_json(f"/appointments/doctor/{doctor_id}", [])
    appt_options = {f"Appt #{a['appointment_id']}: {a.get('patient_name')} ({a.get('appointment_date')})": a for a in appts}
    
    if appt_options:
        default_index = 0
        if active_appt_id:
            for idx, (label, a_obj) in enumerate(appt_options.items()):
                if a_obj["appointment_id"] == active_appt_id:
                    default_index = idx
                    break
        selected_label = st.selectbox("Select Patient Appointment", list(appt_options.keys()), index=default_index)
        sel_appt = appt_options[selected_label]
        appt_id = sel_appt["appointment_id"]
        pat_id = sel_appt["patient_id"]
        hosp_id = sel_appt["hospital_id"]
    else:
        st.warning("No appointments available for this doctor.")
        return

    # Load Pre-Visit Snapshot
    res_snapshot = api_request("GET", f"/previsit/appointment/{appt_id}")
    snapshot = res_snapshot.json() if res_snapshot and res_snapshot.status_code == 200 else {}

    st.markdown("### 🔍 Pre-Visit Clinical Snapshot")
    if snapshot:
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**Patient:** {snapshot.get('patient_name')} | **DOB:** {snapshot.get('date_of_birth')} | **Gender:** {snapshot.get('gender')}")
            st.write(f"**Today's Reported Symptoms:**\n{snapshot.get('todays_symptoms') or 'None reported at check-in'}")
            if snapshot.get("active_allergies"):
                st.error(f"🚨 **ALLERGY ALERT:** {snapshot.get('active_allergies')}")
            else:
                st.success("No active allergies recorded.")

        with c2:
            st.warning(f"**Active Conditions:** {snapshot.get('active_conditions') or 'None on file'}")
            st.write(f"**Ongoing Medications:** {snapshot.get('ongoing_medicines') or 'None'}")
            if snapshot.get("latest_summary"):
                with st.expander("Previous Medical Summary"):
                    st.text(snapshot.get("latest_summary"))
    else:
        st.info("No pre-visit check-in data found for this appointment.")

    st.markdown("---")
    st.markdown("### ✍️ Conduct Clinical Consultation")

    tab_visit, tab_diag, tab_rx, tab_soap, tab_summary = st.tabs([
        "🏥 Clinical Visit & Procedures", "🩺 Diagnoses", "💊 Prescription", "📝 SOAP Notes", "🏁 Conclude & Summary"
    ])

    with tab_visit:
        st.subheader("1. Record Clinical Visit Record")
        with st.form("create_visit_form"):
            c_type, c_complaint = st.columns(2)
            v_type = c_type.selectbox("Visit Type", ["OPD", "IPD", "ER", "Other"])
            c_complaint = c_complaint.text_input("Chief Complaint", value=sel_appt.get("reason") or "")
            vitals = st.text_input("Vitals Summary", placeholder="e.g. BP 120/80, HR 72, Afebrile")
            v_notes = st.text_area("Clinical Examination Notes")

            if st.form_submit_button("Record Clinical Visit", type="primary"):
                payload = {
                    "appointment_id": appt_id,
                    "patient_id": pat_id,
                    "hospital_id": hosp_id,
                    "doctor_id": doctor_id,
                    "visit_date": str(datetime.now().isoformat()),
                    "visit_type": v_type,
                    "chief_complaint": c_complaint,
                    "vitals_summary": vitals,
                    "notes": v_notes
                }
                res = api_request("POST", "/visits", json=payload)
                if res and res.status_code == 201:
                    created_visit_id = res.json().get("visit_id")
                    st.session_state["current_visit_id"] = created_visit_id
                    st.success(f"✅ Clinical Visit recorded! Visit ID: #{created_visit_id}")
                else:
                    st.error("Failed to create visit.")

        st.subheader("2. Record Procedures Performed")
        cur_vid = st.session_state.get("current_visit_id", 1)
        with st.form("add_procedure_form"):
            proc_name = st.text_input("Procedure Name", placeholder="e.g. Nebulization, Wound dressing, ECG")
            proc_notes = st.text_input("Procedure Notes / Outcome")
            if st.form_submit_button("Attach Procedure"):
                payload = {"visit_id": cur_vid, "procedure_name": proc_name, "notes": proc_notes}
                res = api_request("POST", "/visits/procedures", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ Procedure '{proc_name}' attached!")

    with tab_diag:
        st.subheader("Clinical Diagnoses")
        cur_vid = st.session_state.get("current_visit_id", 1)
        with st.form("add_diagnosis_form"):
            c_cond, c_icd = st.columns(2)
            cond_name = c_cond.text_input("Diagnosis Name", placeholder="e.g. Acute Bronchitis, Essential Hypertension")
            icd_code = c_icd.text_input("ICD-10 Code", placeholder="e.g. J20.9, I10")
            diag_type = st.selectbox("Diagnosis Type", ["Primary", "Secondary", "Provisional"])
            notes = st.text_area("Diagnostic Rationale")

            if st.form_submit_button("Record Diagnosis", type="primary"):
                payload = {
                    "visit_id": cur_vid,
                    "diagnosis_name": cond_name,
                    "diagnosis_code": icd_code,
                    "diagnosis_type": diag_type,
                    "notes": notes
                }
                res = api_request("POST", "/visits/diagnoses", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ Diagnosis recorded: **{cond_name}** ({diag_type})")
                else:
                    st.error("Failed to record diagnosis.")

    with tab_rx:
        st.subheader("Prescribe Medication")
        cur_vid = st.session_state.get("current_visit_id", 1)
        with st.form("prescription_form"):
            med_name = st.text_input("Medication Name & Strength", placeholder="e.g. Amoxicillin 500mg, Paracetamol 650mg")
            c_d, c_f, c_dur = st.columns(3)
            dosage = c_d.text_input("Dosage", placeholder="1 tablet")
            freq = c_f.selectbox("Frequency", ["Once daily (1-0-0)", "Twice daily (1-0-1)", "Thrice daily (1-1-1)", "Four times daily", "SOS (As needed)"])
            duration = c_dur.number_input("Duration (Days)", min_value=1, value=5)
            instructions = st.text_input("Instructions", placeholder="Take after food with warm water")

            if st.form_submit_button("Generate Prescription", type="primary"):
                payload = {
                    "visit_id": cur_vid,
                    "patient_id": pat_id,
                    "doctor_id": doctor_id,
                    "prescribed_date": str(date.today()),
                    "items": [
                        {
                            "medicine_name": med_name,
                            "dosage": dosage,
                            "frequency": freq,
                            "duration_days": int(duration),
                            "instructions": instructions
                        }
                    ]
                }
                res = api_request("POST", "/visits/prescriptions", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ Prescribed: **{med_name}** ({duration} days)")
                else:
                    st.error("Failed to save prescription.")

    with tab_soap:
        st.subheader("SOAP Clinical Documentation")
        col_s, col_o = st.columns(2)
        subj = col_s.text_area("Subjective (Symptoms, patient history)", height=120)
        obj = col_o.text_area("Objective (Exam findings, vitals)", height=120)

        col_a, col_p = st.columns(2)
        assess = col_a.text_area("Assessment (Clinical impression)", height=120)
        plan = col_p.text_area("Plan (Medications, diet advice, follow-up)", height=120)

        if st.button("Save SOAP Clinical Note", type="primary"):
            full_note = f"S: {subj}\nO: {obj}\nA: {assess}\nP: {plan}"
            payload = {
                "appointment_id": appt_id,
                "note_text": full_note,
                "added_by": user_info.get("user_id", 1)
            }
            res = api_request("POST", "/appointments/notes", json=payload)
            if res and res.status_code == 201:
                st.success("✅ SOAP Note successfully attached to appointment!")
            else:
                st.error("Failed to save note.")

    with tab_summary:
        st.subheader("Conclude Consultation & Generate Medical Summary")
        col_gen, col_done = st.columns(2)
        with col_gen:
            if st.button("🤖 Generate Episode Medical Summary"):
                res_sum = api_request("POST", f"/summaries/generate/{appt_id}")
                if res_sum and res_sum.status_code in [200, 201]:
                    st.success("✅ Consultation summary generated automatically!")
                    st.json(res_sum.json())
                else:
                    st.info("Automated summary processed.")

        with col_done:
            if st.button("🏁 Finalize & Mark COMPLETED", type="primary"):
                res_status = api_request("PATCH", f"/appointments/{appt_id}/status", json={"status": "Completed"})
                if res_status and res_status.status_code == 200:
                    st.success("🎉 Consultation completed and appointment marked COMPLETED!")
                    st.session_state.pop("active_appointment_id", None)
                    st.rerun()


def doctor_diagnostics_view():
    doctor_id, user_info, _ = _get_doctor_context()
    page_header("Diagnostics & Lab Orders", "🔬", "Order laboratory tests and verify completed pathology & imaging reports")

    tab_order, tab_verify, tab_catalog = st.tabs(["🧪 Order Lab Investigation", "✅ Verify Lab Results", "📋 Test Catalog"])

    with tab_order:
        tests = fetch_json("/diagnostics/tests", [])
        test_map = {f"{t['test_name']} ({t.get('category', 'Lab')})": t["test_id"] for t in tests}

        with st.form("doc_lab_order_form"):
            st.subheader("Create Diagnostic Order")
            v_id = st.number_input("Visit ID / Episode Reference", min_value=1, step=1, value=1)
            selected_tests = st.multiselect("Select Tests to Order", list(test_map.keys()))
            clinical_indication = st.text_area("Clinical Indication", placeholder="Evaluate persistent symptoms...")

            if st.form_submit_button("Dispatch Lab Order", type="primary"):
                if not selected_tests:
                    st.error("Please select at least one test.")
                else:
                    t_ids = [test_map[t] for t in selected_tests]
                    payload = {
                        "visit_id": v_id,
                        "ordered_by": doctor_id,
                        "test_ids": t_ids,
                        "status": "Ordered",
                        "clinical_note": clinical_indication
                    }
                    res = api_request("POST", "/diagnostics/orders", json=payload)
                    if res and res.status_code == 201:
                        st.success(f"✅ Order successfully created! Order ID: #{res.json().get('order_id')}")
                    else:
                        st.error("Failed to submit diagnostic order.")

    with tab_verify:
        st.subheader("Pending Lab Results for Verification")
        results = fetch_json("/diagnostics/results", [])
        pending = [r for r in results if r.get("verification_status") != "Verified"]
        
        if not pending:
            st.success("All lab results have been verified!")
        else:
            for r in pending:
                with st.expander(f"Result #{r.get('result_id')} • {r.get('test_name', 'Lab Test')}"):
                    st.write(f"**Report Date:** {r.get('report_date')}")
                    st.write(f"**Overall Finding:** {r.get('overall_finding')}")
                    st.write(f"**Status:** {r.get('verification_status')}")
                    
                    if st.button("Verify Result", key=f"ver_res_{r.get('result_id')}", type="primary"):
                        res_v = api_request("PUT", f"/diagnostics/results/{r.get('result_id')}/verify?verified_by={user_info.get('user_id', 1)}")
                        if res_v and res_v.status_code == 200:
                            st.success("✅ Result verified!")
                            st.rerun()

    with tab_catalog:
        tests = fetch_json("/diagnostics/tests", [])
        st.dataframe(pd.DataFrame(tests), use_container_width=True, hide_index=True)


def doctor_patient_records_view():
    doctor_id, user_info, _ = _get_doctor_context()
    page_header("Patient EMR & Document Vault", "📂", "Review authorized patient clinical histories, past visits, and uploaded documents")
    
    patients = fetch_json("/identity/patients", [])
    if not patients:
        st.warning("No patients found in directory.")
        return

    pat_map = {f"{p['full_name']} (ID: {p['patient_id']} | Blood: {p.get('blood_group', 'N/A')})": p["patient_id"] for p in patients}
    sel_pat_label = st.selectbox("Search & Select Patient", list(pat_map.keys()))
    pat_id = pat_map[sel_pat_label]

    # Verify Patient Consent Check
    res_consent = api_request("GET", f"/consent/check?patient_id={pat_id}&doctor_id={doctor_id}")
    if res_consent and res_consent.status_code == 200:
        st.success("🛡️ Verified Active Consent: You are authorized to access this patient's medical records.")
    else:
        st.warning("⚠️ Notice: Patient consent status: Standard clinical access granted for consultation.")

    tab_hist, tab_docs = st.tabs(["🩺 Clinical History", "📁 Medical Document Vault"])

    with tab_hist:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Active Conditions")
            conds = fetch_json(f"/visits/patient/{pat_id}/conditions", [])
            if conds:
                st.dataframe(pd.DataFrame(conds), use_container_width=True, hide_index=True)
            else:
                st.info("No active conditions on file.")

        with c2:
            st.markdown("#### Allergies & Adverse Reactions")
            allergies = fetch_json(f"/visits/patient/{pat_id}/allergies", [])
            if allergies:
                st.dataframe(pd.DataFrame(allergies), use_container_width=True, hide_index=True)
            else:
                st.success("No allergies reported.")

    with tab_docs:
        docs = fetch_json(f"/documents/patient/{pat_id}", [])
        if docs:
            for doc in docs:
                with st.expander(f"{doc.get('title')} ({doc.get('verification_status')})"):
                    st.write(f"**MIME:** {doc.get('mime_type')} | **Size:** {round(doc.get('file_size', 0)/1024, 1)} KB")
                    if doc.get("verification_status") != "Verified":
                        if st.button("Mark Document as Verified", key=f"ver_doc_{doc.get('document_id')}"):
                            res_vd = api_request("PATCH", f"/documents/{doc.get('document_id')}/verify")
                            if res_vd and res_vd.status_code == 200:
                                st.success("Document verified.")
                                st.rerun()
        else:
            st.info("No documents uploaded for this patient.")


def doctor_ai_assistant_view():
    page_header("AI Clinical Assistant", "🧠", "Clinical NLP note summarization, symptom extraction, and decision support")

    st.info("💡 Paste raw doctor consultation thoughts, symptoms, or nurse intake logs below. The AI Clinical Engine extracts key symptoms and generates structured recommendations.")

    raw_text = st.text_area(
        "Clinical Input Notes",
        height=180,
        placeholder="Patient reports progressive dry cough since 4 days, low grade evening fever with chills, mild shortness of breath on exertion. Denies chest pain or hemoptysis. BP 128/82, SpO2 97%."
    )

    if st.button("Generate AI Clinical Summary", type="primary"):
        if not raw_text.strip():
            st.warning("Please enter some clinical text to analyze.")
        else:
            with st.spinner("Processing medical NLP analysis..."):
                analysis = generate_mock_summary(raw_text)
                st.markdown(analysis)

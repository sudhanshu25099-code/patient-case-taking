import streamlit as st
import pandas as pd
from datetime import date
from utils.api_client import api_request, fetch_json
from utils.ui_helpers import page_header, render_kpi_card, render_status_badge, check_login


def _get_nurse_context():
    check_login()
    user_info = st.session_state.get("user_info", {})
    nurse = user_info.get("nurse") or {}
    nurse_id = nurse.get("nurse_id")
    
    # If admin simulating nurse view
    if not nurse_id:
        nurses = fetch_json("/identity/nurses", [])
        if nurses:
            nurse_id = nurses[0]["nurse_id"]
            nurse = nurses[0]
            
    return nurse_id, user_info, nurse


def nurse_station_view():
    nurse_id, user_info, nurse = _get_nurse_context()
    page_header(f"Nurse Station • {user_info.get('full_name')}", "👩‍⚕️", f"Shift: {nurse.get('shift', 'Day Shift')} | Employee ID: {nurse.get('employee_no', 'N/A')} | Department: {nurse.get('department_name', 'General Clinic')}")

    appts = fetch_json("/appointments", [])
    scheduled = [a for a in appts if a.get("status") == "Scheduled"]
    completed = [a for a in appts if a.get("status") == "Completed"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Clinic Queue", len(scheduled), "Awaiting Check-in / Doctor", "⏳")
    with c2:
        render_kpi_card("Completed Visits", len(completed), "Concluded Today", "✅")
    with c3:
        render_kpi_card("Total Bookings", len(appts), "Today's Clinic Master", "📅")
    with c4:
        render_kpi_card("Assigned Shift", nurse.get("shift", "Day"), "On Duty", "⏱️")

    st.markdown("---")
    st.subheader("📋 Arriving Patient Queue & Triage Desk")

    if not scheduled:
        st.success("All scheduled patients have been checked in or completed!")
    else:
        for a in scheduled:
            with st.expander(f"🔵 Appt #{a.get('appointment_id')}: {a.get('patient_name')} ({str(a.get('time_slot'))[:5]}) — Dr. {a.get('doctor_name')}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Patient:** {a.get('patient_name')}")
                c1.write(f"**Phone:** {a.get('patient_phone') or 'N/A'}")
                c2.write(f"**Doctor:** Dr. {a.get('doctor_name')} ({a.get('doctor_specialization') or 'General'})")
                c2.write(f"**Hospital:** {a.get('hospital_name')}")
                c3.write(f"**Date & Time:** {a.get('appointment_date')} at {str(a.get('time_slot'))[:5]}")
                c3.write(f"**Reason:** {a.get('reason')}")

                col_btn, _ = st.columns([1, 4])
                with col_btn:
                    if st.button("🩺 Intake & Vitals", key=f"triage_{a.get('appointment_id')}", type="primary"):
                        st.session_state["nurse_active_appt"] = a.get("appointment_id")
                        st.session_state["nurse_active_pat_name"] = a.get("patient_name")
                        st.info("Loaded into Patient Check-In & Pre-Visit! Open the **Check-In & Vitals** tab.")


def nurse_checkin_view():
    nurse_id, user_info, _ = _get_nurse_context()
    page_header("Patient Check-In & Pre-Visit Intake", "⏱️", "Record incoming vitals, presenting symptoms, and triage notes")

    active_aid = st.session_state.get("nurse_active_appt")
    appts = fetch_json("/appointments", [])
    scheduled_appts = [a for a in appts if a.get("status") == "Scheduled"]
    appt_map = {f"Appt #{a['appointment_id']}: {a.get('patient_name')} with Dr. {a.get('doctor_name')}": a["appointment_id"] for a in scheduled_appts}

    if not appt_map:
        st.info("No pending appointments to check in.")
        return

    default_idx = 0
    if active_aid:
        for idx, (lbl, aid) in enumerate(appt_map.items()):
            if aid == active_aid:
                default_idx = idx
                break

    sel_lbl = st.selectbox("Select Patient Appointment", list(appt_map.keys()), index=default_idx)
    sel_aid = appt_map[sel_lbl]

    col_chk, _ = st.columns([1, 3])
    with col_chk:
        if st.button("✅ Mark Patient as Checked-In", type="primary"):
            res_chk = api_request("POST", f"/appointments/{sel_aid}/check-in")
            if res_chk and res_chk.status_code == 200:
                st.success("Patient check-in recorded!")

    tab_vitals, tab_symptoms = st.tabs(["💓 Triage Vitals", "🤒 Presenting Symptoms"])

    with tab_vitals:
        st.subheader("Record Vital Signs")
        with st.form("triage_vitals_form"):
            c_bp, c_pulse, c_temp = st.columns(3)
            bp = c_bp.text_input("Blood Pressure (mmHg)", placeholder="e.g. 120/80")
            pulse = c_pulse.text_input("Pulse Rate (bpm)", placeholder="e.g. 74")
            temp = c_temp.text_input("Body Temperature (°F)", placeholder="e.g. 98.6")

            c_spo2, c_wt, c_ht = st.columns(3)
            spo2 = c_spo2.text_input("SpO2 Oxygen (%)", placeholder="e.g. 98")
            weight = c_wt.text_input("Weight (kg)", placeholder="e.g. 68")
            height = c_ht.text_input("Height (cm)", placeholder="e.g. 172")

            general_obs = st.text_area("General Triage Observation", placeholder="Alert, oriented. Mild pallor observed.")

            if st.form_submit_button("Record Vitals & Log Note", type="primary"):
                vitals_note = f"VITALS: BP: {bp} | Pulse: {pulse} bpm | Temp: {temp}F | SpO2: {spo2}% | Wt: {weight}kg | Ht: {height}cm. Observations: {general_obs}"
                payload = {
                    "appointment_id": sel_aid,
                    "note_text": vitals_note,
                    "added_by": user_info.get("user_id", 1)
                }
                res = api_request("POST", "/appointments/notes", json=payload)
                if res and res.status_code == 201:
                    st.success("✅ Vitals successfully recorded in pre-visit snapshot!")
                else:
                    st.error("Failed to save vitals.")

    with tab_symptoms:
        st.subheader("Add Presenting Symptom")
        with st.form("intake_symptom_form"):
            c_sym, c_sev = st.columns(2)
            sym_name = c_sym.text_input("Symptom", placeholder="e.g. High fever, productive cough, headache")
            severity = c_sev.selectbox("Severity Level", ["Mild", "Moderate", "Severe"])

            c_date, c_dur = st.columns(2)
            since_d = c_date.date_input("Present Since", value=date.today())
            notes = c_dur.text_input("Details / Aggravating factors", placeholder="e.g. Worse at night")

            if st.form_submit_button("Attach Symptom to Pre-Visit Snapshot", type="primary"):
                payload = {
                    "appointment_id": sel_aid,
                    "symptom_name": sym_name,
                    "severity": severity,
                    "since_date": str(since_d),
                    "notes": notes
                }
                res = api_request("POST", "/appointments/symptoms", json=payload)
                if res and res.status_code == 201:
                    st.success(f"✅ Symptom '{sym_name}' attached to appointment pre-visit file!")
                else:
                    st.error("Failed to attach symptom.")


def nurse_care_view():
    page_header("Patient Allergies & Chronic Conditions", "💊", "Record known drug/food allergies and update medical conditions")

    patients = fetch_json("/identity/patients", [])
    if not patients:
        st.warning("No patients found.")
        return

    pat_map = {f"{p['full_name']} (ID: {p['patient_id']})": p["patient_id"] for p in patients}
    sel_pat_lbl = st.selectbox("Select Patient", list(pat_map.keys()))
    pat_id = pat_map[sel_pat_lbl]

    tab_al, tab_cond = st.tabs(["⚠️ Allergies & Alerts", "🩺 Conditions & Chronic Care"])

    with tab_al:
        st.subheader("Existing Allergies")
        allergies = fetch_json(f"/visits/patient/{pat_id}/allergies", [])
        if allergies:
            for al in allergies:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{al.get('allergen')}** ({al.get('allergy_type')}) — Reaction: {al.get('reaction')} | Status: {al.get('status')}")
                if al.get("status") == "Active":
                    if c2.button("Resolve", key=f"res_al_{al.get('allergy_id')}"):
                        res_ra = api_request("PATCH", f"/visits/allergies/{al.get('allergy_id')}/resolve")
                        if res_ra and res_ra.status_code == 200:
                            st.success("Allergy marked as Resolved.")
                            st.rerun()
        else:
            st.info("No allergies on record for this patient.")

        st.markdown("---")
        with st.form("nurse_allergy_form"):
            st.subheader("Add Allergy Alert")
            allergen = st.text_input("Allergen", placeholder="e.g. Penicillin, Peanuts, Sulfa Drugs")
            c_type, c_sev = st.columns(2)
            a_type = c_type.selectbox("Allergy Type", ["Drug", "Food", "Environmental", "Other"])
            severity = c_sev.selectbox("Reaction Severity", ["Mild", "Moderate", "Severe"])
            reaction = st.text_input("Reaction Description", placeholder="e.g. Urticaria, Anaphylaxis, Rash")

            if st.form_submit_button("Add Allergy to Chart", type="primary"):
                payload = {
                    "patient_id": pat_id,
                    "allergen": allergen,
                    "allergy_type": a_type,
                    "severity": severity,
                    "reaction": reaction,
                    "status": "Active"
                }
                res = api_request("POST", "/visits/allergies", json=payload)
                if res and res.status_code == 201:
                    st.success("✅ Allergy added to patient chart!")
                    st.rerun()
                else:
                    st.error("Failed to record allergy.")

    with tab_cond:
        st.subheader("Existing Conditions")
        conds = fetch_json(f"/visits/patient/{pat_id}/conditions", [])
        if conds:
            for cd in conds:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{cd.get('condition_name')}** ({cd.get('condition_type')}) — Status: {cd.get('status')}")
                if cd.get("status") != "Resolved":
                    if c2.button("Mark Resolved", key=f"res_cd_{cd.get('condition_id')}"):
                        res_rc = api_request("PATCH", f"/visits/conditions/{cd.get('condition_id')}/status", json={"status": "Resolved"})
                        if res_rc and res_rc.status_code == 200:
                            st.success("Condition marked as Resolved.")
                            st.rerun()
        else:
            st.info("No chronic conditions registered.")

        st.markdown("---")
        with st.form("nurse_condition_form"):
            st.subheader("Add Chronic / Active Condition")
            cond_name = st.text_input("Condition Name", placeholder="e.g. Type 2 Diabetes, Asthma, Hypertension")
            c_type_cd, c_st_cd = st.columns(2)
            cd_type = c_type_cd.selectbox("Condition Type", ["Chronic", "Past illness", "Surgery", "Family history"])
            status = c_st_cd.selectbox("Status", ["Active", "Controlled", "Resolved"])
            notes = st.text_area("Notes", placeholder="Diagnosed 2021, on oral hypoglycemics")

            if st.form_submit_button("Add Condition", type="primary"):
                payload = {
                    "patient_id": pat_id,
                    "condition_name": cond_name,
                    "condition_type": cd_type,
                    "status": status,
                    "notes": notes
                }
                res = api_request("POST", "/visits/conditions", json=payload)
                if res and res.status_code == 201:
                    st.success("✅ Medical condition recorded!")
                    st.rerun()
                else:
                    st.error("Failed to record condition.")


def nurse_labs_view():
    page_header("Lab Orders & Specimen Tracking", "🧪", "Monitor laboratory orders and specimen collection status")

    tab_orders, tab_results, tab_catalog = st.tabs(["📋 Lab Orders Tracking", "🧪 Enter Test Results", "📖 Test Catalog"])

    with tab_orders:
        orders = fetch_json("/diagnostics/orders", [])
        if orders:
            for ord_item in orders:
                with st.expander(f"Order #{ord_item.get('order_id')} (Status: {ord_item.get('status')})"):
                    st.write(f"**Visit ID:** {ord_item.get('visit_id')} | **Doctor:** {ord_item.get('doctor_name') or 'Physician'}")
                    st.write(f"**Clinical Indication:** {ord_item.get('clinical_note') or 'Routine'}")
                    if ord_item.get("status") == "Ordered":
                        if st.button("Mark Sample Collected / In Progress", key=f"coll_{ord_item.get('order_id')}"):
                            res_up = api_request("PATCH", f"/diagnostics/orders/{ord_item.get('order_id')}/status", json={"status": "Completed"})
                            if res_up and res_up.status_code == 200:
                                st.success("Order status updated.")
                                st.rerun()
        else:
            st.info("No active lab orders.")

    with tab_results:
        with st.form("enter_lab_result_form"):
            st.subheader("Enter Diagnostic Test Finding")
            oi_id = st.number_input("Order Item ID", min_value=1, step=1, value=1)
            finding = st.text_area("Overall Finding / Summary", placeholder="Parameters within standard limits.")

            if st.form_submit_button("Publish Finding", type="primary"):
                payload = {
                    "order_item_id": oi_id,
                    "report_date": str(date.today()),
                    "overall_finding": finding,
                    "verification_status": "Pending",
                    "items": []
                }
                res = api_request("POST", "/diagnostics/results", json=payload)
                if res and res.status_code == 201:
                    st.success("✅ Finding recorded and queued for physician verification!")
                else:
                    st.error("Failed to publish result.")

    with tab_catalog:
        tests = fetch_json("/diagnostics/tests", [])
        st.dataframe(pd.DataFrame(tests), use_container_width=True, hide_index=True)


def nurse_directory_view():
    page_header("Patient Directory & Emergency Contacts", "📇", "Fast lookup of registered patients, blood groups, and emergency info")

    patients = fetch_json("/identity/patients", [])
    if patients:
        df = pd.DataFrame(patients)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No patients currently in directory.")

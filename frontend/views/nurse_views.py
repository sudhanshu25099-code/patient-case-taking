import streamlit as st
import pandas as pd
from datetime import date
from utils.api_client import api_request, fetch_json, handle_action_response
from utils.ui_helpers import (
    page_header, render_kpi_card, render_status_badge, check_login,
    flash_success, flash_error, flash_warning
)


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
    page_header(f"Nurse Station • {user_info.get('full_name')}", ":material/medical_services:", f"Shift: {nurse.get('shift', 'Day Shift')} | Employee ID: {nurse.get('employee_no', 'N/A')} | Department: {nurse.get('department_name', 'General Clinic')}")

    appts = fetch_json("/appointments", [])
    scheduled = [a for a in appts if a.get("status") == "Scheduled"]
    completed = [a for a in appts if a.get("status") == "Completed"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Clinic Queue", len(scheduled), "Awaiting Check-in / Doctor", ":material/hourglass_top:")
    with c2:
        render_kpi_card("Completed Visits", len(completed), "Concluded Today", ":material/check_circle:")
    with c3:
        render_kpi_card("Total Bookings", len(appts), "Today's Clinic Master", ":material/calendar_month:")
    with c4:
        render_kpi_card("Assigned Shift", nurse.get("shift", "Day"), "On Duty", ":material/timer:")

    st.markdown("---")
    st.subheader(":material/assignment: Arriving Patient Queue & Triage Desk")

    if not scheduled:
        st.success("All scheduled patients have been checked in or completed!")
    else:
        for a in scheduled:
            with st.expander(f":material/radio_button_checked: Appt #{a.get('appointment_id')}: {a.get('patient_name')} ({str(a.get('time_slot'))[:5]}) — Dr. {a.get('doctor_name')}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Patient:** {a.get('patient_name')}")
                c1.write(f"**Phone:** {a.get('patient_phone') or 'N/A'}")
                c2.write(f"**Doctor:** Dr. {a.get('doctor_name')} ({a.get('doctor_specialization') or 'General'})")
                c2.write(f"**Hospital:** {a.get('hospital_name')}")
                c3.write(f"**Date & Time:** {a.get('appointment_date')} at {str(a.get('time_slot'))[:5]}")
                c3.write(f"**Reason:** {a.get('reason')}")

                col_btn, _ = st.columns([1, 4])
                with col_btn:
                    if st.button(":material/stethoscope: Intake & Vitals", key=f"triage_{a.get('appointment_id')}", type="primary"):
                        st.session_state["nurse_active_appt"] = a.get("appointment_id")
                        st.session_state["nurse_active_pat_name"] = a.get("patient_name")
                        st.info("Loaded into Patient Check-In & Pre-Visit! Open the **Check-In & Vitals** tab.")


def nurse_checkin_view():
    nurse_id, user_info, _ = _get_nurse_context()
    page_header("Patient Check-In & Pre-Visit Intake", ":material/timer:", "Record incoming vitals, presenting symptoms, and triage notes")

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
        if st.button(":material/check_circle: Mark Patient as Checked-In", type="primary"):
            res_chk = api_request("POST", f"/appointments/{sel_aid}/check-in")
            handle_action_response(
                res_chk,
                success_msg=f"Patient check-in recorded for Appointment #{sel_aid}!",
                error_prefix="Failed to record check-in",
                rerun=True
            )

    tab_vitals, tab_symptoms = st.tabs([":material/cardiology: Triage Vitals", ":material/sick: Presenting Symptoms"])

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
                handle_action_response(
                    res,
                    success_msg=f"Vitals & triage observations recorded for Appointment #{sel_aid}!",
                    error_prefix="Failed to save vitals",
                    rerun=True
                )

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
                if not sym_name.strip():
                    flash_warning("Please provide a symptom description.")
                    st.rerun()
                payload = {
                    "appointment_id": sel_aid,
                    "symptom_name": sym_name.strip(),
                    "severity": severity,
                    "since_date": str(since_d),
                    "notes": notes
                }
                res = api_request("POST", "/appointments/symptoms", json=payload)
                handle_action_response(
                    res,
                    success_msg=f"Symptom '{sym_name}' attached to appointment pre-visit file!",
                    error_prefix="Failed to attach symptom",
                    rerun=True
                )


def nurse_care_view():
    page_header("Patient Allergies & Chronic Conditions", ":material/medication:", "Record known drug/food allergies and update medical conditions")

    patients = fetch_json("/identity/patients", [])
    if not patients:
        st.warning("No patients found.")
        return

    pat_map = {f"{p['full_name']} (ID: {p['patient_id']})": p["patient_id"] for p in patients}
    sel_pat_lbl = st.selectbox("Select Patient", list(pat_map.keys()))
    pat_id = pat_map[sel_pat_lbl]

    tab_al, tab_cond = st.tabs([":material/warning: Allergies & Alerts", ":material/stethoscope: Conditions & Chronic Care"])

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
                        handle_action_response(
                            res_ra,
                            success_msg=f"Allergy '{al.get('allergen')}' resolved successfully!",
                            error_prefix="Failed to resolve allergy",
                            rerun=True
                        )
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
                if not allergen.strip():
                    flash_warning("Please enter allergen name.")
                    st.rerun()
                payload = {
                    "patient_id": pat_id,
                    "allergen": allergen.strip(),
                    "allergy_type": a_type,
                    "severity": severity,
                    "reaction": reaction,
                    "status": "Active"
                }
                res = api_request("POST", "/visits/allergies", json=payload)
                handle_action_response(
                    res,
                    success_msg=f"Allergy '{allergen}' added to patient chart!",
                    error_prefix="Failed to record allergy",
                    rerun=True
                )

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
                        handle_action_response(
                            res_rc,
                            success_msg=f"Condition '{cd.get('condition_name')}' marked as Resolved!",
                            error_prefix="Failed to resolve condition",
                            rerun=True
                        )
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
                if not cond_name.strip():
                    flash_warning("Please provide a condition name.")
                    st.rerun()
                payload = {
                    "patient_id": pat_id,
                    "condition_name": cond_name.strip(),
                    "condition_type": cd_type,
                    "status": status,
                    "notes": notes
                }
                res = api_request("POST", "/visits/conditions", json=payload)
                handle_action_response(
                    res,
                    success_msg=f"Medical condition '{cond_name}' recorded in patient chart!",
                    error_prefix="Failed to record condition",
                    rerun=True
                )


def nurse_labs_view():
    page_header("Lab Orders & Specimen Tracking", ":material/experiment:", "Monitor laboratory orders, track specimens, and record diagnostic test findings")

    tab_orders, tab_results, tab_catalog = st.tabs([":material/assignment: Lab Orders Tracking", ":material/experiment: Enter Test Results", ":material/menu_book: Test Catalog"])

    with tab_orders:
        orders = fetch_json("/diagnostics/orders", [])
        if orders:
            for ord_item in orders:
                oid = ord_item.get("order_id")
                st_badge = ord_item.get("status")
                with st.expander(f"Order #{oid} — Status: {st_badge} • Dr. {ord_item.get('doctor_name') or 'Physician'}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Visit ID:** #{ord_item.get('visit_id')} | **Order Date:** {str(ord_item.get('order_date'))[:16]}")
                    c2.write(f"**Clinical Indication:** {ord_item.get('clinical_note') or 'Routine investigation'}")

                    # List items under this order
                    items = fetch_json(f"/diagnostics/orders/{oid}/items", [])
                    if items:
                        st.markdown("**Ordered Investigations:**")
                        for it in items:
                            st.markdown(f"- **Item #{it.get('order_item_id')}**: Test ID #{it.get('test_id')} — *Status: {it.get('status')}*")

                    if ord_item.get("status") == "Ordered":
                        if st.button("Mark Sample Collected / In Progress", key=f"coll_{oid}"):
                            res_up = api_request("PATCH", f"/diagnostics/orders/{oid}/status", json={"status": "Completed"})
                            handle_action_response(
                                res_up,
                                success_msg=f"Order #{oid} specimen marked as collected!",
                                error_prefix="Failed to update order status",
                                rerun=True
                            )
        else:
            st.info("No active lab orders.")

    with tab_results:
        st.subheader("Record Diagnostic Test Findings")
        order_items = fetch_json("/diagnostics/order-items", [])

        if not order_items:
            st.info("No diagnostic test orders found in the system.")
        else:
            only_pending = st.checkbox("Show only pending test items without results", value=True)
            display_items = [i for i in order_items if not i.get("result_id")] if only_pending else order_items

            if not display_items:
                st.success("All test items currently have results published! Uncheck 'Show only pending' above to review or update existing findings.")
            else:
                def item_display(i):
                    pat = i.get('patient_name') or f"Visit #{i.get('visit_id')}"
                    t_name = i.get('test_name') or f"Test #{i.get('test_id')}"
                    cat = i.get('category') or 'Lab'
                    has_res = "✓ Recorded" if i.get("result_id") else "⏳ Pending Result"
                    return f"Item #{i['order_item_id']} (Order #{i['order_id']}) • {t_name} [{cat}] — {pat} ({has_res})"

                selected_item = st.selectbox("Select Test Order Item to Record Result", display_items, format_func=item_display)

                if selected_item:
                    is_done = bool(selected_item.get("result_id"))
                    border_color = "#16a34a" if is_done else "#0284c7"
                    bg_color = "#f0fdf4" if is_done else "#f8fafc"

                    st.markdown(f"""
                    <div style="background-color: {bg_color}; border: 1px solid #cbd5e1; border-left: 5px solid {border_color}; padding: 14px 18px; border-radius: 8px; margin: 12px 0 20px 0;">
                        <h4 style="margin: 0 0 8px 0; color: #0f172a;">{selected_item.get('test_name')} ({selected_item.get('category')})</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.95em; color: #334155;">
                            <div><strong>Patient:</strong> {selected_item.get('patient_name') or 'N/A'}</div>
                            <div><strong>Ordering Doctor:</strong> Dr. {selected_item.get('doctor_name') or 'Physician'}</div>
                            <div><strong>Order Ref:</strong> Order #{selected_item.get('order_id')} (Item #{selected_item.get('order_item_id')})</div>
                            <div><strong>Order Date:</strong> {str(selected_item.get('order_date'))[:16]}</div>
                        </div>
                        <div style="margin-top: 8px; font-size: 0.9em; color: #475569;">
                            <strong>Clinical Indication:</strong> <em>{selected_item.get('clinical_note') or 'None specified'}</em>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    existing_finding = selected_item.get("overall_finding") or ""

                    with st.form("enter_lab_result_form"):
                        report_dt = st.date_input("Report Date", value=date.today())
                        finding = st.text_area(
                            "Overall Finding / Summary",
                            value=existing_finding,
                            height=130,
                            placeholder="e.g. All parameters within standard physiological limits. No acute pathology observed."
                        )

                        btn_label = "Update Diagnostic Finding" if is_done else "Publish Diagnostic Finding"
                        if st.form_submit_button(btn_label, type="primary"):
                            if not finding.strip():
                                flash_warning("Please enter a summary of the test findings before publishing.")
                                st.rerun()

                            payload = {
                                "order_item_id": selected_item["order_item_id"],
                                "report_date": str(report_dt),
                                "overall_finding": finding.strip(),
                                "verification_status": "Pending",
                                "items": []
                            }
                            res = api_request("POST", "/diagnostics/results", json=payload)
                            handle_action_response(
                                res,
                                success_msg=f"Diagnostic finding for '{selected_item.get('test_name')}' (Item #{selected_item['order_item_id']}) recorded and forwarded for doctor verification!",
                                error_prefix="Failed to publish result",
                                rerun=True
                            )

    with tab_catalog:
        tests = fetch_json("/diagnostics/tests", [])
        st.dataframe(pd.DataFrame(tests), use_container_width=True, hide_index=True)


def nurse_directory_view():
    page_header("Patient Directory & Emergency Contacts", ":material/contacts:", "Fast lookup of registered patients, blood groups, and emergency info")

    patients = fetch_json("/identity/patients", [])
    if patients:
        df = pd.DataFrame(patients)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No patients currently in directory.")

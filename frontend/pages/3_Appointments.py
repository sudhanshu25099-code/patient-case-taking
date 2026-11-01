"""
Appointments & Pre-Visit Care Gateway
Handles Appointment Booking, Status Transitions, Symptom Recording, Notes, and 360-Degree Pre-Visit Snapshots.
"""

import streamlit as st
import pandas as pd
from datetime import date, time, datetime

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge
from utils.ai_engine import ai_engine

st.set_page_config(page_title="Appointments & Pre-Visit • HealthPulse", page_icon="📅", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="Appointments & Pre-Visit Gateway",
    subtitle="Interactive Scheduling, Patient Intake, Triage Check-in, and 360° Clinical Pre-Visit Briefings",
    badge_text="Module 3",
    icon="📅"
)

tabs = st.tabs(["📅 Master Schedule", "➕ Book Appointment", "📝 Log Symptoms & Notes", "🔍 360° Pre-Visit Snapshot"])

# ------------------------------------------------------------------------------
# TAB 1: MASTER SCHEDULE
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 📅 Clinical Appointments Schedule")
    
    appts = client.list_appointments()
    
    f1, f2, f3 = st.columns(3)
    with f1:
        status_filter = st.selectbox("Status Filter", ["All", "Scheduled", "In Progress", "Completed", "Cancelled"])
    with f2:
        docs = client.list_doctors()
        doc_opts = {0: "All Doctors"}
        doc_opts.update({d["doctor_id"]: d["full_name"] for d in docs})
        doc_filter = st.selectbox("Doctor Filter", options=list(doc_opts.keys()), format_func=lambda x: doc_opts.get(x))
    with f3:
        pats = client.list_patients()
        pat_opts = {0: "All Patients"}
        pat_opts.update({p["patient_id"]: p["full_name"] for p in pats})
        pat_filter = st.selectbox("Patient Filter", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

    filtered_appts = appts
    if status_filter != "All":
        filtered_appts = [a for a in filtered_appts if a.get("status") == status_filter]
    if doc_filter != 0:
        filtered_appts = [a for a in filtered_appts if a.get("doctor_id") == doc_filter]
    if pat_filter != 0:
        filtered_appts = [a for a in filtered_appts if a.get("patient_id") == pat_filter]

    st.markdown(f"**Found {len(filtered_appts)} Appointments**")

    for a in filtered_appts:
        with st.container():
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.15rem; margin-bottom: 0.85rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">{a.get('patient_name', 'Patient')}</span>
                        <span style="color: #64748b; font-size: 0.9rem;">with</span>
                        <span style="font-size: 1.05rem; font-weight: 700; color: #0284c7;">{a.get('doctor_name', 'Doctor')}</span>
                        <span style="margin-left: 0.5rem;">{render_status_badge(a.get('status', 'Scheduled'))}</span>
                    </div>
                    <div style="font-weight: 700; color: #334155; font-size: 0.95rem;">
                        🗓️ {a.get('appointment_date')} at {str(a.get('time_slot'))[:5]}
                    </div>
                </div>
                <div style="font-size: 0.875rem; color: #475569; margin-top: 0.4rem;">
                    <strong>Reason for Consultation:</strong> {a.get('reason', 'Routine review')}
                </div>
                {f"<div style='font-size: 0.825rem; color: #64748b; margin-top: 0.2rem;'><strong>Pre-Visit Notes:</strong> {a.get('pre_visit_notes')}</div>" if a.get('pre_visit_notes') else ""}
            </div>
            """, unsafe_allow_html=True)

            # Actions row
            c_act1, c_act2, c_act3, c_act4 = st.columns([1, 1, 1, 2])
            with c_act1:
                if a.get("status") == "Scheduled":
                    if st.button("Check-In 📍", key=f"ci_{a['appointment_id']}", use_container_width=True):
                        client.check_in_appointment(a["appointment_id"])
                        st.success(f"Appointment #{a['appointment_id']} marked as In Progress!")
                        st.rerun()
            with c_act2:
                if a.get("status") in ("Scheduled", "In Progress"):
                    if st.button("Complete ✅", key=f"comp_{a['appointment_id']}", use_container_width=True):
                        client.update_appointment_status(a["appointment_id"], "Completed")
                        st.success("Appointment completed!")
                        st.rerun()
            with c_act3:
                if a.get("status") in ("Scheduled", "In Progress"):
                    if st.button("Cancel ❌", key=f"canc_{a['appointment_id']}", use_container_width=True):
                        client.update_appointment_status(a["appointment_id"], "Cancelled")
                        st.warning("Appointment cancelled.")
                        st.rerun()
            with c_act4:
                if st.button("View 360° Pre-Visit Snapshot 🔍", key=f"pv_{a['appointment_id']}", use_container_width=True):
                    st.session_state["selected_snapshot_appt"] = a["appointment_id"]
                    st.info(f"Loaded Snapshot for Appointment #{a['appointment_id']}. Switch to the '360° Pre-Visit Snapshot' tab to view details.")

# ------------------------------------------------------------------------------
# TAB 2: BOOK APPOINTMENT
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### ➕ Schedule a New Patient Appointment")
    
    with st.form("book_appointment_form"):
        pats = client.list_patients()
        pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']} - Blood: {p.get('blood_group','')})" for p in pats}
        selected_patient = st.selectbox("Select Patient", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

        hosps = client.list_hospitals()
        hosp_opts = {h["hospital_id"]: h["name"] for h in hosps}
        selected_hospital = st.selectbox("Hospital / Clinic Location", options=list(hosp_opts.keys()), format_func=lambda x: hosp_opts.get(x))

        docs = client.list_doctors()
        doc_opts = {d["doctor_id"]: f"{d['full_name']} ({d['specialization']} - Fee: ₹{d.get('consultation_fee',0)})" for d in docs}
        selected_doctor = st.selectbox("Attending Physician", options=list(doc_opts.keys()), format_func=lambda x: doc_opts.get(x))

        c_dt1, c_dt2 = st.columns(2)
        with c_dt1:
            appt_date = st.date_input("Appointment Date", value=date.today())
        with c_dt2:
            time_slot = st.selectbox("Preferred Time Slot", ["09:00:00", "09:30:00", "10:00:00", "10:30:00", "11:00:00", "11:30:00", "14:00:00", "14:30:00", "15:00:00", "16:00:00"])

        reason = st.text_input("Primary Reason for Visit", placeholder="e.g. Chest tightness, hypertension followup, knee pain...")
        pre_notes = st.text_area("Patient Intake / Pre-Visit Notes", placeholder="e.g. Symptoms worse after exertion, bringing blood sugar diary...")
        is_follow_up = st.checkbox("This is a follow-up consultation", value=False)

        st.markdown("##### Initial Symptoms Log (Optional)")
        sym_col1, sym_col2 = st.columns(2)
        with sym_col1:
            sym_name = st.text_input("Reported Symptom", placeholder="e.g. Shortness of breath")
        with sym_col2:
            sym_sev = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])

        if st.form_submit_button("Confirm & Book Appointment", type="primary", use_container_width=True):
            if reason.strip():
                new_appt = client.create_appointment({
                    "patient_id": selected_patient,
                    "hospital_id": selected_hospital,
                    "doctor_id": selected_doctor,
                    "appointment_date": str(appt_date),
                    "time_slot": time_slot,
                    "reason": reason,
                    "pre_visit_notes": pre_notes,
                    "is_follow_up": is_follow_up,
                    "status": "Scheduled"
                })
                # If symptom entered, log it
                if sym_name.strip():
                    client.add_appointment_symptom({
                        "appointment_id": new_appt["appointment_id"],
                        "symptom_name": sym_name,
                        "severity": sym_sev,
                        "since_date": str(appt_date)
                    })
                st.success(f"Appointment successfully confirmed! Appointment ID: #{new_appt['appointment_id']}")
                st.rerun()
            else:
                st.error("Please specify the primary reason for consultation.")

# ------------------------------------------------------------------------------
# TAB 3: LOG SYMPTOMS & NOTES
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 📝 Log Intake Symptoms & Clinical Pre-Notes")
    
    appts = client.list_appointments()
    active_appts = [a for a in appts if a.get("status") in ("Scheduled", "In Progress")]
    
    if active_appts:
        appt_select_opts = {
            a["appointment_id"]: f"#{a['appointment_id']} - {a.get('patient_name')} with {a.get('doctor_name')} ({a.get('appointment_date')})"
            for a in active_appts
        }
        target_appt_id = st.selectbox("Select Active Appointment", options=list(appt_select_opts.keys()), format_func=lambda x: appt_select_opts.get(x))

        c_sym, c_note = st.columns(2)

        with c_sym:
            st.markdown("#### 🩺 Add Symptom Record")
            with st.form("add_symptom_form"):
                s_name = st.text_input("Symptom Name", placeholder="e.g. Palpitations, Dizziness, Cough")
                s_sev = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
                s_date = st.date_input("Onset Date", value=date.today())
                s_notes = st.text_input("Notes / Trigger Details", placeholder="e.g. Occurs after meals or exertion")

                if st.form_submit_button("Record Symptom", use_container_width=True):
                    if s_name:
                        client.add_appointment_symptom({
                            "appointment_id": target_appt_id,
                            "symptom_name": s_name,
                            "severity": s_sev,
                            "since_date": str(s_date),
                            "notes": s_notes
                        })
                        st.success(f"Symptom '{s_name}' logged for appointment #{target_appt_id}!")
                        st.rerun()

        with c_note:
            st.markdown("#### 📝 Add Pre-Encounter Clinical Note")
            with st.form("add_appt_note_form"):
                note_content = st.text_area("Intake Note / Triage Observations", placeholder="e.g. Vitals checked at reception: BP 130/85, Pulse 82. Patient appears comfortable.")
                author_id = st.session_state.get("active_doctor_id", 2)

                if st.form_submit_button("Attach Clinical Note", use_container_width=True):
                    if note_content.strip():
                        client.add_appointment_note({
                            "appointment_id": target_appt_id,
                            "note_text": note_content,
                            "added_by": author_id
                        })
                        st.success("Note attached to appointment!")
                        st.rerun()

        # Display current symptoms & notes
        st.markdown("---")
        appt_detail = client.get_appointment(target_appt_id)
        if appt_detail:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("##### Recorded Symptoms for this Appointment")
                syms = appt_detail.get("symptoms", [])
                if syms:
                    for s in syms:
                        st.markdown(f"- **{s.get('symptom_name')}** ({s.get('severity')}) — Since: {s.get('since_date')} *{s.get('notes','')}*")
                else:
                    st.caption("No specific symptoms recorded yet.")
            with col_d2:
                st.markdown("##### Attached Pre-Visit Notes")
                notes = appt_detail.get("notes", [])
                if notes:
                    for n in notes:
                        st.markdown(f"- 📌 *\"{n.get('note_text')}\"* <span style='font-size:0.75rem; color:#64748b;'>({n.get('added_at','')[:16]})</span>", unsafe_allow_html=True)
                else:
                    st.caption("No triage notes attached yet.")
    else:
        st.info("No scheduled or in-progress appointments available to record intake data.")

# ------------------------------------------------------------------------------
# TAB 4: 360° PRE-VISIT SNAPSHOT
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 🔍 360-Degree Pre-Visit Clinical Snapshot")
    st.caption("Leverages database pre-visit views to consolidate patient history, active allergies, chronic conditions, and ongoing medications before entering the exam room.")

    appts = client.list_appointments()
    appt_opts = {a["appointment_id"]: f"#{a['appointment_id']} - {a.get('patient_name')} ({a.get('appointment_date')} - {a.get('reason')})" for a in appts}
    
    default_id = st.session_state.get("selected_snapshot_appt", list(appt_opts.keys())[0] if appt_opts else 1)
    if default_id not in appt_opts and appt_opts:
        default_id = list(appt_opts.keys())[0]

    selected_snapshot_id = st.selectbox("Select Patient Appointment Snapshot", options=list(appt_opts.keys()), index=list(appt_opts.keys()).index(default_id) if default_id in appt_opts else 0, format_func=lambda x: appt_opts.get(x))

    if selected_snapshot_id:
        snap = client.get_previsit_snapshot(selected_snapshot_id)
        if snap:
            st.markdown(f"""
            <div class="glass-card" style="border-top: 4px solid #0284c7; padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem;">
                    <div>
                        <span style="font-size: 1.35rem; font-weight: 800; color: #0f172a;">{snap.get('patient_name')}</span>
                        <span style="font-size: 0.85rem; color: #64748b; margin-left: 0.5rem;">(Patient ID: #{snap.get('patient_id')})</span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0284c7;">
                        🗓️ Consultation: {snap.get('appointment_date')} at {str(snap.get('time_slot'))[:5]}
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-top: 1rem;">
                    <div>
                        <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Primary Consultation Reason</div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-top: 0.2rem;">{snap.get('reason', 'N/A')}</div>
                        
                        <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-top: 0.85rem;">Today's Reported Symptoms</div>
                        <div style="font-size: 0.95rem; color: #334155; margin-top: 0.2rem;">{snap.get('todays_symptoms')}</div>

                        <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-top: 0.85rem;">Pre-Visit Triage Notes</div>
                        <div style="font-size: 0.95rem; color: #334155; margin-top: 0.2rem;">{snap.get('pre_visit_notes', 'None recorded')}</div>
                    </div>

                    <div style="background: #f8fafc; padding: 1rem; border-radius: 10px; border: 1px solid #e2e8f0;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #dc2626; text-transform: uppercase;">🚨 Documented Allergies</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #991b1b; margin-top: 0.2rem;">{snap.get('active_allergies')}</div>

                        <div style="font-size: 0.8rem; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-top: 0.85rem;">🩺 Active Chronic Conditions</div>
                        <div style="font-size: 0.95rem; color: #0f172a; margin-top: 0.2rem;">{snap.get('active_conditions')}</div>

                        <div style="font-size: 0.8rem; font-weight: 700; color: #16a34a; text-transform: uppercase; margin-top: 0.85rem;">💊 Ongoing Prescriptions</div>
                        <div style="font-size: 0.95rem; color: #0f172a; margin-top: 0.2rem;">{snap.get('ongoing_medicines')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # AI Clinical Briefing Action
            st.markdown("#### ✨ AI Pre-Visit Clinical Briefing")
            if st.button("Generate AI Executive Briefing", type="primary", use_container_width=True):
                patient_data = client.get_patient(snap["patient_id"]) or {"patient_id": snap["patient_id"], "full_name": snap["patient_name"]}
                allergies = client.get_patient_allergies(snap["patient_id"])
                conditions = client.get_patient_conditions(snap["patient_id"])
                
                with st.spinner("AI synthesizing multi-system clinical data..."):
                    briefing = ai_engine.generate_previsit_briefing(patient_data, allergies, conditions, [snap])
                    st.markdown(briefing)

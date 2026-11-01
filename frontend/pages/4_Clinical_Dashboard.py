"""
Clinical Dashboard & Case Taking Workspace
Provides clinical encounter recording, vitals, SOAP notes, diagnoses, procedures,
e-prescriptions with drug-allergy safety scanner, and chronic disease tracking.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge
from utils.ai_engine import ai_engine

st.set_page_config(page_title="Clinical Dashboard • HealthPulse", page_icon="🩺", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="Clinical Case Taking & Encounter Workspace",
    subtitle="Vitals Monitoring, SOAP Consultation Notes, ICD Diagnoses, e-Prescriptions & Safety Verification",
    badge_text="Module 4",
    icon="🩺"
)

# Patient & Active Visit Selector
patients = client.list_patients()
pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']} - Blood: {p.get('blood_group','')})" for p in patients}

col_sel1, col_sel2 = st.columns([1.5, 1.5])
with col_sel1:
    default_p = st.session_state.get("active_patient_id", 4)
    if default_p not in pat_opts:
        default_p = list(pat_opts.keys())[0] if pat_opts else 1
    selected_patient_id = st.selectbox(
        "Active Patient for Clinical Encounter",
        options=list(pat_opts.keys()),
        index=list(pat_opts.keys()).index(default_p) if default_p in pat_opts else 0,
        format_func=lambda x: pat_opts.get(x)
    )
    st.session_state["active_patient_id"] = selected_patient_id

with col_sel2:
    patient_visits = client.list_patient_visits(selected_patient_id)
    visit_opts = {0: "➕ Start New Clinical Encounter"}
    visit_opts.update({v["visit_id"]: f"Visit #{v['visit_id']} ({v.get('visit_date','')[:10]} - {v.get('chief_complaint','')[:35]}...)" for v in patient_visits})
    
    selected_visit_id = st.selectbox(
        "Select Clinical Encounter",
        options=list(visit_opts.keys()),
        format_func=lambda x: visit_opts.get(x)
    )

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

tabs = st.tabs([
    "🩺 1. Intake & Vitals",
    "📝 2. SOAP Notes",
    "🔬 3. Diagnoses & Procedures",
    "💊 4. e-Prescription Pad",
    "🚨 5. Allergies & Conditions",
    "📄 6. Full Case Sheet"
])

# ------------------------------------------------------------------------------
# TAB 1: INTAKE & VITALS
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 🩺 Clinical Intake, Case Taking & Objective Vitals")
    
    with st.form("encounter_intake_form"):
        col_type, col_doc, col_hosp = st.columns(3)
        with col_type:
            v_type = st.selectbox("Encounter Type", ["OPD", "IPD", "ER", "Other"])
        with col_doc:
            docs = client.list_doctors()
            doc_opts = {d["doctor_id"]: f"{d['full_name']} ({d['specialization']})" for d in docs}
            v_doc = st.selectbox("Attending Doctor", options=list(doc_opts.keys()), format_func=lambda x: doc_opts.get(x))
        with col_hosp:
            hosps = client.list_hospitals()
            hosp_opts = {h["hospital_id"]: h["name"] for h in hosps}
            v_hosp = st.selectbox("Hospital / Clinic Facility", options=list(hosp_opts.keys()), format_func=lambda x: hosp_opts.get(x))

        chief_complaint = st.text_area("Chief Complaint (Reason for encounter)", placeholder="e.g. 45-year-old female presents with persistent dry cough and wheezing for 2 weeks...")
        symptoms_desc = st.text_input("Detailed Symptoms & Aggravating Factors", placeholder="e.g. Expiratory wheeze, aggravated by night cold dust, relieved partly with steam.")

        st.markdown("##### 📊 Physical Examination & Vitals Triage")
        v1, v2, v3, v4, v5 = st.columns(5)
        with v1:
            bp_sys = st.number_input("Systolic BP (mmHg)", 60, 260, 120)
            bp_dia = st.number_input("Diastolic BP (mmHg)", 40, 160, 80)
        with v2:
            pulse = st.number_input("Pulse Rate (bpm)", 30, 200, 78)
            spo2 = st.number_input("SpO2 Room Air (%)", 50, 100, 98)
        with v3:
            temp = st.number_input("Temp (°F)", 94.0, 107.0, 98.4, 0.1)
            resp = st.number_input("Resp Rate (/min)", 8, 50, 16)
        with v4:
            height = st.number_input("Height (cm)", 50, 250, 165)
            weight = st.number_input("Weight (kg)", 20.0, 300.0, 68.0, 0.5)
        with v5:
            # Calculate BMI
            bmi = round(weight / ((height / 100) ** 2), 1)
            bmi_cat = "Normal" if 18.5 <= bmi <= 24.9 else ("Overweight" if 25 <= bmi <= 29.9 else ("Obese" if bmi >= 30 else "Underweight"))
            st.metric("Calculated BMI", f"{bmi} kg/m²", bmi_cat)

        vitals_formatted = f"BP: {bp_sys}/{bp_dia} mmHg | Pulse: {pulse} bpm | SpO2: {spo2}% | Temp: {temp} °F | Resp: {resp}/min | Height: {height}cm | Weight: {weight}kg | BMI: {bmi} ({bmi_cat})"

        notes = st.text_area("Clinical Examination Observations", placeholder="e.g. Chest: Bilateral breath sounds present, scattered rhonchi in lower zones. CVS: S1 S2 normal.")

        if st.form_submit_button("Record Clinical Encounter", type="primary", use_container_width=True):
            if chief_complaint.strip():
                new_v = client.create_visit({
                    "patient_id": selected_patient_id,
                    "hospital_id": v_hosp,
                    "doctor_id": v_doc,
                    "visit_date": datetime.now().isoformat(),
                    "visit_type": v_type,
                    "chief_complaint": chief_complaint,
                    "symptoms": symptoms_desc,
                    "vitals_summary": vitals_formatted,
                    "notes": notes
                })
                st.success(f"Encounter #{new_v['visit_id']} successfully registered in EHR!")
                st.rerun()
            else:
                st.error("Please enter the chief complaint.")

# ------------------------------------------------------------------------------
# TAB 2: SOAP NOTES
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 📝 Structured SOAP Consultation Notes")
    active_vid = selected_visit_id if selected_visit_id != 0 else (patient_visits[0]["visit_id"] if patient_visits else None)
    
    if not active_vid:
        st.warning("Please record or select an existing clinical encounter above to manage SOAP notes.")
    else:
        current_visit = client.get_visit(active_vid) or {}
        st.markdown(f"**Documenting Notes for Encounter #{active_vid}** — *{current_visit.get('chief_complaint', '')}*")

        c_soap_left, c_soap_right = st.columns([1.3, 1.3])

        with c_soap_left:
            st.markdown("#### ✨ AI Assist: Auto-Generate Clinical SOAP Draft")
            st.caption("AI analyzes the encounter's symptoms and patient profile to draft standard SOAP documentation.")
            
            if st.button("Generate AI SOAP Consultation Note", type="primary", use_container_width=True):
                patient_rec = client.get_patient(selected_patient_id)
                allergies = client.get_patient_allergies(selected_patient_id)
                conditions = client.get_patient_conditions(selected_patient_id)
                
                context = {
                    "full_name": patient_rec.get("full_name") if patient_rec else "Patient",
                    "allergies": ", ".join([a["allergen"] for a in allergies]) if allergies else "NKDA",
                    "conditions": ", ".join([c["condition_name"] for c in conditions]) if conditions else "None"
                }
                
                analysis = ai_engine.analyze_symptoms(current_visit.get("chief_complaint", "Clinical evaluation"), context)
                st.session_state[f"ai_soap_{active_vid}"] = analysis["soap_note"]
                st.success("AI SOAP note synthesized!")

            prefill_soap = st.session_state.get(f"ai_soap_{active_vid}", "")
            with st.form("manual_soap_form"):
                note_title = st.text_input("Note Title", value="Comprehensive Consultation Note")
                note_type = st.selectbox("Note Type", ["Consultation", "Follow-up", "Other"])
                soap_text = st.text_area("SOAP Content (Subjective, Objective, Assessment, Plan)", value=prefill_soap, height=220)
                
                if st.form_submit_button("Save SOAP Note to Patient Chart", use_container_width=True):
                    if soap_text.strip():
                        client.add_visit_note({
                            "visit_id": active_vid,
                            "note_type": note_type,
                            "title": note_title,
                            "content": soap_text,
                            "added_by": current_visit.get("doctor_id", 1)
                        })
                        st.success("Note saved to clinical chart!")
                        st.rerun()

        with c_soap_right:
            st.markdown("#### 📂 Charted Notes for this Visit")
            notes = client.list_visit_notes(active_vid)
            if notes:
                for n in notes:
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 1rem; margin-bottom: 0.65rem;">
                        <div style="display: flex; justify-content: space-between;">
                            <strong style="color: #0284c7;">{n.get('title', 'Clinical Note')}</strong>
                            <span class="badge badge-active">{n.get('note_type', 'Consultation')}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.2rem;">
                            Recorded: {n.get('added_at','')[:16]}
                        </div>
                        <div class="soap-box" style="margin-top: 0.5rem;">{n.get('content')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No SOAP notes charted for this visit yet. Use the form on the left to add one.")

# ------------------------------------------------------------------------------
# TAB 3: DIAGNOSES & PROCEDURES
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🔬 Diagnoses & Clinical Procedures")
    active_vid = selected_visit_id if selected_visit_id != 0 else (patient_visits[0]["visit_id"] if patient_visits else None)

    if not active_vid:
        st.warning("Please record or select an encounter first.")
    else:
        col_diag, col_proc = st.columns(2)

        with col_diag:
            st.markdown("#### 🩺 ICD-10 Diagnoses")
            with st.form("add_diagnosis_form"):
                diag_code = st.text_input("ICD-10 Code", placeholder="e.g. J45.909, I20.9, E11.9, M17.9")
                diag_name = st.text_input("Diagnosis Name", placeholder="e.g. Bronchial Asthma, Unspecified")
                diag_type = st.selectbox("Diagnosis Type", ["Primary", "Secondary", "Provisional"])
                diag_notes = st.text_input("Clinical Staging / Severity Notes", placeholder="e.g. Moderate persistent, allergic component")

                if st.form_submit_button("Add Diagnosis to Visit", type="primary", use_container_width=True):
                    if diag_name:
                        client.add_diagnosis({
                            "visit_id": active_vid,
                            "diagnosis_code": diag_code,
                            "diagnosis_name": diag_name,
                            "diagnosis_type": diag_type,
                            "notes": diag_notes
                        })
                        st.success(f"Diagnosis '{diag_name}' recorded!")
                        st.rerun()

            st.markdown("##### Current Diagnoses for Encounter")
            existing_diags = client.list_diagnoses(active_vid)
            if existing_diags:
                for ed in existing_diags:
                    st.markdown(f"- 🏷️ **{ed.get('diagnosis_name')}** (`{ed.get('diagnosis_code','N/A')}`) — *{ed.get('diagnosis_type')}* ({ed.get('notes','')})")
            else:
                st.caption("No diagnoses added to this visit yet.")

        with col_proc:
            st.markdown("#### 🛠️ Clinical Procedures Performed")
            with st.form("add_procedure_form"):
                proc_name = st.text_input("Procedure Name", placeholder="e.g. Spirometry, ECG, Wound Debridement, Nebulization")
                proc_type = st.selectbox("Procedure Type", ["Diagnostic", "Therapeutic", "Minor Surgical"])
                proc_notes = st.text_input("Outcome / Observations", placeholder="e.g. FEV1 improved by 16% post bronchodilator")

                if st.form_submit_button("Record Procedure", use_container_width=True):
                    if proc_name:
                        client.add_procedure({
                            "visit_id": active_vid,
                            "procedure_name": proc_name,
                            "procedure_type": proc_type,
                            "notes": proc_notes
                        })
                        st.success(f"Procedure '{proc_name}' saved!")
                        st.rerun()

            st.markdown("##### Procedures Performed for Encounter")
            existing_procs = client.list_procedures(active_vid)
            if existing_procs:
                for ep in existing_procs:
                    st.markdown(f"- ⚙️ **{ep.get('procedure_name')}** ({ep.get('procedure_type')}) — *{ep.get('notes','')}*")
            else:
                st.caption("No procedures performed in this visit.")

# ------------------------------------------------------------------------------
# TAB 4: e-PRESCRIPTION PAD & DRUG-ALLERGY SCANNER
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 💊 e-Prescription Pad & AI Safety Scanner")
    active_vid = selected_visit_id if selected_visit_id != 0 else (patient_visits[0]["visit_id"] if patient_visits else None)

    if not active_vid:
        st.warning("Please record or select an encounter first.")
    else:
        cur_v = client.get_visit(active_vid) or {}
        p_allergies = client.get_patient_allergies(selected_patient_id)
        p_conditions = client.get_patient_conditions(selected_patient_id)

        # Active Safety Alert Banner
        if p_allergies:
            st.markdown(f"""
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem;">
                <strong style="color: #b91c1c;">🚨 Patient Allergy Alert:</strong> 
                <span style="color: #7f1d1d;">{', '.join([a['allergen'] + f" ({a['severity']})" for a in p_allergies])}</span>
            </div>
            """, unsafe_allow_html=True)

        col_rx_write, col_rx_view = st.columns([1.5, 1.2])

        with col_rx_write:
            st.markdown("#### ✍️ Issue Prescription")
            
            with st.form("new_prescription_form"):
                st.markdown("##### Medication Item Details")
                med_name = st.text_input("Medication Name & Strength", placeholder="e.g. Budesonide 200mcg Inhaler, Amoxicillin 500mg, Metformin 500mg")
                
                c_rx1, c_rx2 = st.columns(2)
                with c_rx1:
                    dosage = st.text_input("Dosage Unit", placeholder="e.g. 1 puff, 1 tablet, 10 ml")
                    frequency = st.selectbox("Frequency", ["Once daily", "Twice daily (BID)", "Three times daily (TID)", "Four times daily (QID)", "SOS / When required", "At bedtime (HS)"])
                    route = st.selectbox("Route", ["Oral", "Inhalation", "Intravenous", "Subcutaneous", "Topical"])
                with c_rx2:
                    duration_days = st.number_input("Duration (Days)", min_value=1, max_value=365, value=14)
                    is_ongoing = st.checkbox("Mark as Ongoing Chronic Therapy", value=False)
                    instructions = st.text_input("Special Instructions", placeholder="e.g. Take after meals, with a full glass of water")

                rx_general_notes = st.text_input("Prescription Header / General Advice", placeholder="e.g. Maintain hydration, avoid dust exposure")

                submit_rx = st.form_submit_button("Review Safety & Issue Prescription", type="primary", use_container_width=True)
                
                if submit_rx:
                    if med_name.strip():
                        # Run AI Drug Safety Scanner
                        safety_check = ai_engine.check_drug_safety(med_name, p_allergies, p_conditions)
                        
                        if not safety_check["is_safe"]:
                            st.error(f"⛔ SAFETY INTERACTION DETECTED FOR '{med_name}'!")
                            for w in safety_check["warnings"]:
                                st.error(f"**{w['severity']}** — {w['type']}: {w['detail']}")
                        else:
                            if safety_check["has_warnings"]:
                                for w in safety_check["warnings"]:
                                    st.warning(f"**{w['severity']}**: {w['detail']}")

                            # Create prescription
                            rx_payload = {
                                "visit_id": active_vid,
                                "patient_id": selected_patient_id,
                                "doctor_id": cur_v.get("doctor_id", 1),
                                "prescribed_date": str(date.today()),
                                "notes": rx_general_notes,
                                "items": [
                                    {
                                        "medicine_name": med_name,
                                        "dosage": dosage,
                                        "frequency": frequency,
                                        "route": route,
                                        "duration_days": duration_days,
                                        "is_ongoing": is_ongoing,
                                        "instructions": instructions
                                    }
                                ]
                            }
                            res = client.create_prescription(rx_payload)
                            st.success(f"Prescription #{res['prescription_id']} issued successfully!")
                            st.rerun()
                    else:
                        st.error("Please enter medicine name.")

        with col_rx_view:
            st.markdown("#### 📜 Existing Prescriptions for Patient")
            patient_rx = [pr for pr in client.mock_db["prescriptions"] if pr.get("patient_id") == selected_patient_id]
            if patient_rx:
                for pr in patient_rx:
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 1rem; margin-bottom: 0.75rem; border-left: 4px solid #10b981;">
                        <div style="display: flex; justify-content: space-between;">
                            <strong style="color: #0f172a;">Prescription #{pr.get('prescription_id')}</strong>
                            <span style="font-size: 0.8rem; color: #64748b;">🗓️ {pr.get('prescribed_date')}</span>
                        </div>
                        <div style="font-size: 0.825rem; color: #475569; margin-top: 0.35rem;">
                            <strong>Advice:</strong> {pr.get('notes', 'Standard regimen')}
                        </div>
                        <div style="margin-top: 0.5rem; border-top: 1px solid #f1f5f9; padding-top: 0.4rem;">
                    """, unsafe_allow_html=True)
                    for it in pr.get("items", []):
                        st.markdown(f"- 💊 **{it.get('medicine_name')}** ({it.get('dosage')}, {it.get('frequency')}) for {it.get('duration_days')} days. *\"{it.get('instructions','')}\"*")
                    st.markdown("</div></div>", unsafe_allow_html=True)
            else:
                st.info("No prescriptions recorded for this patient yet.")

# ------------------------------------------------------------------------------
# TAB 5: ALLERGIES & CHRONIC CONDITIONS
# ------------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### 🚨 Allergies & Chronic Conditions Tracker")
    
    col_al, col_cond = st.columns(2)

    with col_al:
        st.markdown("#### Documented Allergies")
        allergies = client.get_patient_allergies(selected_patient_id)
        if allergies:
            for al in allergies:
                st.markdown(f"""
                <div class="glass-card" style="padding: 0.85rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #dc2626;">⚠️ {al.get('allergen')}</span>
                        {render_status_badge(al.get('status', 'Active'))}
                    </div>
                    <div style="font-size: 0.825rem; color: #475569; margin-top: 0.25rem;">
                        <strong>Type:</strong> {al.get('allergy_type')} | <strong>Reaction:</strong> {al.get('reaction')} | <strong>Severity:</strong> {al.get('severity')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if al.get("status") == "Active":
                    if st.button(f"Mark Resolved: {al.get('allergen')}", key=f"res_al_{al['allergy_id']}"):
                        client.resolve_allergy(al["allergy_id"])
                        st.success(f"Allergy '{al.get('allergen')}' marked as resolved!")
                        st.rerun()
        else:
            st.info("No recorded drug or food allergies.")

        with st.expander("➕ Add New Patient Allergy"):
            with st.form("new_allergy_form"):
                allergen = st.text_input("Allergen (Drug / Substance)", placeholder="e.g. Penicillin, Sulfa, Aspirin, Peanuts")
                al_type = st.selectbox("Allergy Category", ["Drug", "Food", "Environmental", "Other"])
                reaction = st.text_input("Clinical Reaction", placeholder="e.g. Hives, facial swelling, anaphylaxis")
                severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
                notes = st.text_input("Notes", placeholder="e.g. Diagnosed in 2021 after oral amoxicillin")

                if st.form_submit_button("Save Allergy", type="primary", use_container_width=True):
                    if allergen:
                        client.add_allergy({
                            "patient_id": selected_patient_id,
                            "allergen": allergen,
                            "allergy_type": al_type,
                            "reaction": reaction,
                            "severity": severity,
                            "noted_date": str(date.today()),
                            "notes": notes
                        })
                        st.success(f"Allergy '{allergen}' saved!")
                        st.rerun()

    with col_cond:
        st.markdown("#### Active Chronic Conditions")
        conditions = client.get_patient_conditions(selected_patient_id)
        if conditions:
            for c in conditions:
                st.markdown(f"""
                <div class="glass-card" style="padding: 0.85rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #0f172a;">🩺 {c.get('condition_name')}</span>
                        {render_status_badge(c.get('status', 'Active'))}
                    </div>
                    <div style="font-size: 0.825rem; color: #475569; margin-top: 0.25rem;">
                        <strong>ICD:</strong> <code>{c.get('icd_code', 'N/A')}</code> | <strong>Onset:</strong> {c.get('onset_date')} | <strong>Type:</strong> {c.get('condition_type')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_st1, c_st2 = st.columns(2)
                with c_st1:
                    if c.get("status") != "Controlled" and st.button(f"Set Controlled", key=f"ctrl_{c['condition_id']}"):
                        client.update_condition_status(c["condition_id"], "Controlled")
                        st.success("Status updated to Controlled")
                        st.rerun()
                with c_st2:
                    if c.get("status") != "Resolved" and st.button(f"Set Resolved", key=f"res_{c['condition_id']}"):
                        client.update_condition_status(c["condition_id"], "Resolved")
                        st.success("Status updated to Resolved")
                        st.rerun()
        else:
            st.info("No chronic conditions recorded.")

        with st.expander("➕ Add Chronic Condition"):
            with st.form("new_cond_form"):
                cond_name = st.text_input("Condition Name", placeholder="e.g. Type 2 Diabetes, Hypertension, Asthma")
                icd = st.text_input("ICD-10 Code", placeholder="e.g. E11.9, I10, J45.909")
                c_type = st.selectbox("Condition Type", ["Chronic", "Past illness", "Surgery", "Family history"])
                onset = st.date_input("Onset Date", value=date(2020, 1, 1))
                cond_status = st.selectbox("Status", ["Active", "Controlled", "Resolved"])

                if st.form_submit_button("Record Condition", type="primary", use_container_width=True):
                    if cond_name:
                        client.add_condition({
                            "patient_id": selected_patient_id,
                            "condition_name": cond_name,
                            "icd_code": icd,
                            "condition_type": c_type,
                            "onset_date": str(onset),
                            "status": cond_status
                        })
                        st.success(f"Condition '{cond_name}' recorded!")
                        st.rerun()

# ------------------------------------------------------------------------------
# TAB 6: FULL CASE SHEET
# ------------------------------------------------------------------------------
with tabs[5]:
    st.markdown("### 📄 Patient Clinical Case Sheet & Encounter Summary")
    
    patient = client.get_patient(selected_patient_id)
    allergies = client.get_patient_allergies(selected_patient_id)
    conditions = client.get_patient_conditions(selected_patient_id)
    all_visits = client.list_patient_visits(selected_patient_id)
    all_rx = [pr for pr in client.mock_db["prescriptions"] if pr.get("patient_id") == selected_patient_id]

    st.markdown(f"""
    <div style="background: white; border: 2px solid #cbd5e1; border-radius: 12px; padding: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #0284c7; padding-bottom: 1rem;">
            <div>
                <h2 style="margin: 0; color: #0f172a;">HEALTHPULSE CLINICAL CASE SHEET</h2>
                <div style="color: #64748b; font-size: 0.85rem;">Official Electronic Health Record • Confidential Medical Document</div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #0284c7;">PATIENT ID #{selected_patient_id}</div>
                <div style="font-size: 0.85rem; color: #475569;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.25rem; background: #f8fafc; padding: 1rem; border-radius: 8px;">
            <div>
                <strong>Patient Name:</strong> {patient.get('full_name', 'Patient')}<br>
                <strong>Blood Group:</strong> {patient.get('blood_group', 'N/A')}<br>
                <strong>ABHA Linked:</strong> {'Yes' if patient.get('abha_linked') else 'No'}
            </div>
            <div>
                <strong>Emergency Contact:</strong> {patient.get('emergency_contact_name', 'None')}<br>
                <strong>Emergency Phone:</strong> {patient.get('emergency_contact_phone', 'None')}
            </div>
            <div>
                <strong>Known Allergies:</strong> {', '.join([a['allergen'] for a in allergies]) if allergies else 'NKDA'}<br>
                <strong>Active Conditions:</strong> {', '.join([c['condition_name'] for c in conditions]) if conditions else 'None'}
            </div>
        </div>

        <h4 style="margin-top: 1.5rem; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem;">Encounter History ({len(all_visits)} Visits)</h4>
    """, unsafe_allow_html=True)

    for v in all_visits:
        st.markdown(f"""
        <div style="margin-top: 0.75rem; padding: 0.75rem; border-left: 3px solid #0284c7; background: #fafafa;">
            <strong>Visit #{v['visit_id']} ({v.get('visit_date','')[:10]} - {v.get('visit_type')})</strong> with {v.get('doctor_name','Doctor')}<br>
            <strong>Chief Complaint:</strong> {v.get('chief_complaint')}<br>
            <strong>Vitals:</strong> <code>{v.get('vitals_summary')}</code><br>
            <strong>Observations:</strong> {v.get('notes')}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <h4 style="margin-top: 1.5rem; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem;">Active Medications & Prescriptions</h4>
    """, unsafe_allow_html=True)

    if all_rx:
        for pr in all_rx:
            for it in pr.get("items", []):
                st.markdown(f"- 💊 **{it.get('medicine_name')}** — {it.get('dosage')} | {it.get('frequency')} | {it.get('route')} ({it.get('instructions','')})")
    else:
        st.caption("No active medications prescribed.")

    st.markdown("</div>", unsafe_allow_html=True)

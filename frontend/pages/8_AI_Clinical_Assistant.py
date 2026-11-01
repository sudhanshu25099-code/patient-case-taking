"""
AI Clinical Intelligence Suite
Clean and beautiful AI Assistant for Medical Case Taking, Differential Diagnosis,
Pre-Visit Chart Synthesis, Drug-Allergy Safety Scans, and Lab Biomarker Explanation.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge
from utils.ai_engine import ai_engine

st.set_page_config(page_title="AI Clinical Assistant • HealthPulse", page_icon="✨", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="AI Clinical Intelligence & Case Taking Suite",
    subtitle="Conversational Intake, Differential Diagnosis, Drug Safety Scanning & 360° Chart Synthesis",
    badge_text="Clinical AI v2.5",
    icon="✨"
)

tabs = st.tabs([
    "💬 1. AI Case Taker & Symptom Intake",
    "🩺 2. Patient 360° Chart Briefing",
    "🛡️ 3. Drug-Allergy Safety Scanner",
    "🧪 4. Lab Report Explainer",
    "📚 5. Clinical Knowledge Q&A"
])

# ------------------------------------------------------------------------------
# TAB 1: AI CASE TAKER & SYMPTOM INTAKE
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 💬 Conversational Case Taking & Differential Diagnosis")
    st.caption("Enter patient presentation or clinical chief complaints. The AI parses symptoms, infers differential diagnoses, screens for red flags, and synthesizes a structured SOAP note.")

    # Quick clinical case templates for instant demo
    st.markdown("##### 💡 Or Select a Clinical Scenario Template:")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    
    preset_symptom = ""
    with t_col1:
        if st.button("Cardiology: Angina", use_container_width=True):
            preset_symptom = "52-year-old male with retrosternal squeezing chest pain, radiating to left arm and jaw on climbing stairs. Accompanied by diaphoresis and palpitations."
    with t_col2:
        if st.button("Pulmonology: Asthma", use_container_width=True):
            preset_symptom = "28-year-old female presenting with nocturnal cough, shortness of breath, and bilateral expiratory wheezing aggravated by cold weather."
    with t_col3:
        if st.button("Endocrinology: Diabetes", use_container_width=True):
            preset_symptom = "46-year-old male reporting polyuria, polydipsia, unexplainable fatigue, dry mouth, and progressive weight loss over the past 6 weeks."
    with t_col4:
        if st.button("Neurology: Migraine", use_container_width=True):
            preset_symptom = "34-year-old female complaining of recurrent unilateral throbbing temporal headache, preceded by zigzag visual aura, nausea, and severe photophobia."

    # Text Area
    user_input = st.text_area(
        "Enter Patient Clinical Presentation / Symptoms",
        value=preset_symptom if preset_symptom else st.session_state.get("case_input_text", ""),
        height=110,
        placeholder="Type or paste symptoms (e.g. 50yo presenting with severe chest tightness, diaphoresis, radiating pain to left arm...)"
    )

    col_btn, col_pat_ctx = st.columns([1.2, 1.8])
    with col_pat_ctx:
        patients = client.list_patients()
        pat_opts = {0: "General / Unspecified Patient"}
        pat_opts.update({p["patient_id"]: f"{p['full_name']} (Blood: {p.get('blood_group','')})" for p in patients})
        ctx_pat_id = st.selectbox("Attach Patient Context (Optional)", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

    with col_btn:
        run_analysis = st.button("Run AI Clinical Reasoning", type="primary", use_container_width=True)

    if run_analysis or preset_symptom:
        if user_input.strip():
            # Build patient context
            ctx = None
            if ctx_pat_id != 0:
                p_obj = client.get_patient(ctx_pat_id)
                al = client.get_patient_allergies(ctx_pat_id)
                cd = client.get_patient_conditions(ctx_pat_id)
                ctx = {
                    "full_name": p_obj.get("full_name") if p_obj else "Patient",
                    "allergies": ", ".join([a["allergen"] for a in al]) if al else "NKDA",
                    "conditions": ", ".join([c["condition_name"] for c in cd]) if cd else "None"
                }

            with st.spinner("AI evaluating pathophysiological patterns and differential matrix..."):
                analysis = ai_engine.analyze_symptoms(user_input, ctx)

            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Results layout
            c_res1, c_res2 = st.columns([1.4, 1.4])

            with c_res1:
                st.markdown(f"""
                <div class="glass-card" style="border-top: 4px solid #0284c7; padding: 1.25rem;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Primary Differential Diagnosis</div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #0f172a; margin-top: 0.2rem;">
                        {analysis['top_condition']}
                    </div>
                    <div style="margin-top: 0.35rem;">
                        <span class="badge badge-active">ICD-10: {analysis['icd_code']}</span>
                        <span class="badge badge-scheduled" style="margin-left: 0.4rem;">Triage: {analysis['triage']}</span>
                    </div>

                    <div style="margin-top: 1rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem;">
                        <strong style="color: #dc2626; font-size: 0.9rem;">🚨 Red Flag Warnings:</strong>
                        <ul style="margin: 0.35rem 0 0 1.25rem; color: #7f1d1d; font-size: 0.85rem;">
                            {''.join([f"<li>{rf}</li>" for rf in analysis['red_flags']])}
                        </ul>
                    </div>

                    <div style="margin-top: 1rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem;">
                        <strong style="color: #0284c7; font-size: 0.9rem;">🧪 Recommended Diagnostic Investigations:</strong>
                        <div style="margin-top: 0.35rem;">
                            {''.join([f"<span class='badge' style='background:#f0f9ff; color:#0369a1; border:1px solid #bae6fd; margin-right:6px; margin-bottom:4px;'>{t}</span>" for t in analysis['recommended_tests']])}
                        </div>
                    </div>

                    <div style="margin-top: 1rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem;">
                        <strong style="color: #1e293b; font-size: 0.9rem;">❓ Suggested Interview Questions:</strong>
                        <ul style="margin: 0.35rem 0 0 1.25rem; color: #334155; font-size: 0.85rem;">
                            {''.join([f"<li>{q}</li>" for q in analysis['targeted_questions']])}
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c_res2:
                st.markdown("#### 📄 Synthesized Clinical SOAP Note")
                st.markdown(f"<div class='soap-box' style='height: 380px; overflow-y: auto;'>{analysis['soap_note']}</div>", unsafe_allow_html=True)
                if st.button("Copy Note to Clinical Dashboard", use_container_width=True):
                    st.session_state["copied_soap"] = analysis["soap_note"]
                    st.success("Note copied! You can paste it into the Clinical Dashboard notes.")
        else:
            st.warning("Please type patient symptoms above or click one of the preset scenarios.")

# ------------------------------------------------------------------------------
# TAB 2: PATIENT 360° CHART BRIEFING
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 🩺 Patient 360° AI Clinical Briefing")
    st.caption("Select any patient in the database to generate an executive clinical summary synthesizing chronic conditions, allergies, ongoing medicines, and risk factors.")

    patients = client.list_patients()
    pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']} - Blood: {p.get('blood_group','')})" for p in patients}
    b_patient_id = st.selectbox("Select Patient Profile", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x), key="brief_pat")

    if st.button("Generate AI Pre-Visit Briefing", type="primary", use_container_width=True):
        p_data = client.get_patient(b_patient_id)
        al = client.get_patient_allergies(b_patient_id)
        cd = client.get_patient_conditions(b_patient_id)
        appts = client.list_appointments(patient_id=b_patient_id)

        with st.spinner("AI analyzing longitudinal medical records..."):
            briefing = ai_engine.generate_previsit_briefing(p_data, al, cd, appts)
            st.markdown(briefing)

# ------------------------------------------------------------------------------
# TAB 3: DRUG-ALLERGY SAFETY SCANNER
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🛡️ Drug-Allergy & Clinical Interaction Safety Scanner")
    st.caption("Verifies candidate prescriptions against the patient's documented drug allergies and active chronic conditions prior to dispensing.")

    patients = client.list_patients()
    pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']})" for p in patients}
    d_patient_id = st.selectbox("Target Patient", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x), key="drug_pat")

    p_al = client.get_patient_allergies(d_patient_id)
    p_cd = client.get_patient_conditions(d_patient_id)

    c_al_disp, c_cd_disp = st.columns(2)
    with c_al_disp:
        st.markdown(f"**Known Allergies:** `{', '.join([a['allergen'] for a in p_al]) if p_al else 'NKDA'}`")
    with c_cd_disp:
        st.markdown(f"**Active Conditions:** `{', '.join([c['condition_name'] for c in p_cd]) if p_cd else 'None'}`")

    med_test = st.text_input("Enter Proposed Medication Candidate", placeholder="e.g. Amoxicillin 500mg, Propranolol 40mg, Ibuprofen 400mg, Metformin 500mg")

    if st.button("Run Safety Scan", type="primary", use_container_width=True):
        if med_test.strip():
            result = ai_engine.check_drug_safety(med_test, p_al, p_cd)
            
            if not result["is_safe"]:
                st.markdown(f"""
                <div style="background: #fef2f2; border: 2px solid #ef4444; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
                    <h3 style="color: #b91c1c; margin: 0;">⛔ SEVERE CONTRAINDICATION DETECTED</h3>
                    <div style="color: #7f1d1d; font-size: 0.95rem; margin-top: 0.5rem;">
                        <strong>'{med_test}'</strong> conflicts with patient's documented profile:
                    </div>
                    <ul style="color: #991b1b; margin-top: 0.4rem;">
                        {''.join([f"<li><strong>{w['severity']}</strong> — {w['type']}: {w['detail']}</li>" for w in result['warnings']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                if result["has_warnings"]:
                    st.markdown(f"""
                    <div style="background: #fffbeb; border: 2px solid #f59e0b; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
                        <h3 style="color: #b45309; margin: 0;">⚠️ PRECAUTION ADVISED</h3>
                        <div style="color: #78350f; font-size: 0.95rem; margin-top: 0.5rem;">
                            Medication may be administered with close clinical monitoring:
                        </div>
                        <ul style="color: #92400e; margin-top: 0.4rem;">
                            {''.join([f"<li><strong>{w['severity']}</strong> — {w['type']}: {w['detail']}</li>" for w in result['warnings']])}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
                        <h3 style="color: #15803d; margin: 0;">✅ SAFETY CLEARANCE APPROVED</h3>
                        <div style="color: #166534; font-size: 0.95rem; margin-top: 0.5rem;">
                            No contraindications or drug-allergy conflicts detected for <strong>'{med_test}'</strong>.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Please enter a medicine name to test.")

# ------------------------------------------------------------------------------
# TAB 4: LAB REPORT EXPLAINER
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 🧪 AI Lab Report & Biomarker Explainer")
    st.caption("Translates diagnostic values into both physician-oriented assessments and empathetic, plain-English explanations for patients.")

    c_lexp1, c_lexp2, c_lexp3 = st.columns(3)
    with c_lexp1:
        param = st.selectbox("Biomarker Parameter", ["HbA1c", "Total Cholesterol", "Hemoglobin", "TSH", "WBC Count", "Serum Creatinine"])
    with c_lexp2:
        val = st.text_input("Reported Value", value="8.2")
    with c_lexp3:
        flag = st.selectbox("Flag Status", ["High", "Normal", "Low"])

    if st.button("Generate Dual Explanations", type="primary", use_container_width=True):
        expl = ai_engine.explain_lab_result(
            test_name="Diagnostic Test",
            param_name=param,
            value=val,
            flag=flag,
            unit="%" if param == "HbA1c" else "mg/dL",
            ref_range="4.0 - 5.6" if param == "HbA1c" else "< 200"
        )

        st.markdown("#### 🩺 Physician Clinical Insight")
        st.info(expl["doctor_insight"])

        st.markdown("#### 💬 Plain-English Patient Explanation")
        st.success(expl["patient_translation"])

# ------------------------------------------------------------------------------
# TAB 5: CLINICAL KNOWLEDGE Q&A
# ------------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### 📚 Clinical Knowledge & Protocol Q&A")
    st.caption("Ask clinical guidelines, triage algorithms, dosage calculations, and emergency protocols.")

    sample_questions = [
        "What are the diagnostic criteria for Type 2 Diabetes based on HbA1c and FPG?",
        "What are the first-line treatment steps for an acute asthma exacerbation?",
        "When is an ECG indicated in non-cardiac surgery pre-operative clearance?",
        "What are the red flags requiring urgent MRI in acute headache presentations?"
    ]

    selected_q = st.selectbox("Suggested Clinical Guidelines", sample_questions)
    custom_q = st.text_input("Or Ask a Custom Medical Query", value=selected_q)

    if st.button("Consult Medical Knowledge Base", type="primary", use_container_width=True):
        with st.spinner("Retrieving evidence-based clinical protocols..."):
            if "asthma" in custom_q.lower():
                st.markdown("""
                #### 📋 Evidence-Based Protocol: Acute Bronchial Asthma Exacerbation
                1. **Oxygenation:** Administer supplemental O2 via nasal cannula or mask to maintain SpO2 **93% - 95%**.
                2. **Short-Acting Beta-2 Agonist (SABA):** Inhaled Albuterol / Salbutamol (4-8 puffs via MDI with spacer, or 2.5-5mg nebulized every 20 mins for 3 doses).
                3. **Anticholinergic:** Add Ipratropium Bromide (0.5mg nebulized) for moderate-to-severe exacerbations.
                4. **Systemic Corticosteroids:** Oral Prednisolone (40-50mg) or IV Hydrocortisone (100mg) early to accelerate recovery.
                5. **Monitoring:** Peak Expiratory Flow (PEF), respiratory rate, and continuous pulse oximetry.
                """)
            elif "diabetes" in custom_q.lower():
                st.markdown("""
                #### 📋 Diagnostic Criteria: Type 2 Diabetes Mellitus (ADA Guidelines)
                - **HbA1c:** ≥ **6.5%** (performed in an NGSP-certified laboratory)
                - **Fasting Plasma Glucose (FPG):** ≥ **126 mg/dL** (7.0 mmol/L) after at least 8 hours of fasting.
                - **2-Hour Oral Glucose Tolerance Test (OGTT):** ≥ **200 mg/dL** (11.1 mmol/L) using 75g anhydrous glucose.
                - **Random Plasma Glucose:** ≥ **200 mg/dL** in the presence of classic symptoms of hyperglycemia (polyuria, polydipsia, weight loss).
                """)
            elif "headache" in custom_q.lower():
                st.markdown("""
                #### 🚨 SNOOP4 Red Flags in Headache (Indications for Urgent Neuroimaging)
                - **S**ystemic symptoms (fever, weight loss) or secondary risk factors (HIV, malignancy).
                - **N**eurological signs or symptoms (confusion, impaired alertness, focal cranial nerve deficits).
                - **O**nset sudden or abrupt ("thunderclap headache" peaking within 60 seconds).
                - **O**lder age at onset (> 50 years with new headache pattern).
                - **P**attern change or progression (postural headache, Valsalva-induced, or papilledema).
                """)
            else:
                st.markdown(f"""
                #### 📖 Clinical Summary for: *"{custom_q}"*
                - **Guideline Consensus:** Follow standard institutional protocol and individualize therapy according to patient comorbidities, renal function, and age.
                - **Diagnostic Workup:** Baseline vitals, complete blood count, and targeted organ function profiling recommended.
                - **Safety:** Always cross-reference with documented drug allergies before initiating new pharmaceutical interventions.
                """)

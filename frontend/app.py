"""
HealthPulse • Patient Case Taking & Healthcare Record System
Main Executive Dashboard & Clinical Command Center
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_metric_card, render_status_badge, render_sidebar_context
from utils.ai_engine import ai_engine


st.set_page_config(
    page_title="HealthPulse • Case Taking & Records",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
render_sidebar_context(client)

# Header
render_header(
    title="Clinical Command Center",
    subtitle="Secure Patient Case Taking, Multi-Hospital Records, Diagnostics & AI Clinical Assistant",
    badge_text="FastAPI + MySQL",
    icon="🏥"
)

# ------------------------------------------------------------------------------
# EXECUTIVE KPI METRICS
# ------------------------------------------------------------------------------
patients = client.list_patients()
doctors = client.list_doctors()
appointments = client.list_appointments()
tests = client.list_diagnostic_tests()
consents = client.mock_db.get("consents", [])

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_metric_card("Total Patients", len(patients), "Registered in EHR", icon="👥")
with col2:
    render_metric_card("Active Doctors", len(doctors), "Across 3 Hospitals", icon="👨‍⚕️")
with col3:
    render_metric_card("Appointments", len(appointments), "Scheduled & Active", icon="📅")
with col4:
    render_metric_card("Lab Catalog", len(tests), "Standard Panels", icon="🧪")
with col5:
    render_metric_card("Consents Active", len([c for c in consents if c.get("status") == "Active"]), "Patient Authorized", icon="🛡️")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# QUICK NAVIGATION CARDS
# ------------------------------------------------------------------------------
st.markdown("### ⚡ Quick Navigation Hub")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0284c7; margin-bottom: 0.25rem;">👤 1. Identity & Profiles</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Manage Patients, Doctors, Nurses, User Accounts & Roles.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Identity Directory", key="btn_nav_id", use_container_width=True):
        st.switch_page("pages/1_Identity_&_Profiles.py")

with nav_col2:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0284c7; margin-bottom: 0.25rem;">🏛️ 2. Hospital Admin</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Configure Facilities, Departments, and Doctor Affiliations.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Hospital Admin", key="btn_nav_hosp", use_container_width=True):
        st.switch_page("pages/2_Hospital_Admin.py")

with nav_col3:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0284c7; margin-bottom: 0.25rem;">📅 3. Appointments</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Schedule visits, log symptoms, check-in, and view pre-visit briefs.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Appointments Hub", key="btn_nav_appt", use_container_width=True):
        st.switch_page("pages/3_Appointments.py")

with nav_col4:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0284c7; margin-bottom: 0.25rem;">🩺 4. Clinical Dashboard</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">In-depth case taking, SOAP notes, prescriptions, and diagnosis.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Clinical Encounter", key="btn_nav_clin", use_container_width=True):
        st.switch_page("pages/4_Clinical_Dashboard.py")

nav_col5, nav_col6, nav_col7, nav_col8 = st.columns(4)

with nav_col5:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0284c7; margin-bottom: 0.25rem;">🧪 5. Lab & Diagnostics</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Order tests, input parameters, verify results, and monitor trends.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Diagnostics", key="btn_nav_lab", use_container_width=True):
        st.switch_page("pages/5_Lab_&_Diagnostics.py")

with nav_col6:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0284c7; margin-bottom: 0.25rem;">📁 6. Document Vault</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Secure medical repository for PDFs, Scans, Prescriptions & OCR.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Document Vault", key="btn_nav_doc", use_container_width=True):
        st.switch_page("pages/6_Document_Vault.py")

with nav_col7:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0284c7; margin-bottom: 0.25rem;">🛡️ 7. Consent Management</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Manage patient authorization, doctor access, and audit trails.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Consent Gateway", key="btn_nav_cons", use_container_width=True):
        st.switch_page("pages/7_Consent_Management.py")

with nav_col8:
    st.markdown("""
    <div class="glass-card" style="padding: 1.25rem; border: 1.5px solid #c084fc; background: #faf5ff;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #9333ea; margin-bottom: 0.25rem;">✨ 8. AI Clinical Assistant</div>
        <div style="font-size: 0.85rem; color: #7e22ce; margin-bottom: 0.75rem;">Differential diagnosis, drug allergy scanner & chart summaries.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch AI Suite", key="btn_nav_ai", use_container_width=True):
        st.switch_page("pages/8_AI_Clinical_Assistant.py")

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TWO COLUMN WORKSPACE: UPCOMING QUEUE + QUICK AI TRIAGE
# ------------------------------------------------------------------------------
left_col, right_col = st.columns([1.6, 1.2])

with left_col:
    st.markdown("""
    <div class="glass-card">
        <div class="glass-card-header">
            <span>📅 Priority Appointments & Schedule</span>
        </div>
    """, unsafe_allow_html=True)
    
    appts = client.list_appointments()
    if appts:
        for a in appts[:4]:
            st.markdown(f"""
            <div style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 0.85rem 1rem; border-radius: 6px; margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">
                        {a.get('patient_name', 'Patient')} <span style="font-weight: 400; color: #64748b;">with</span> {a.get('doctor_name', 'Doctor')}
                    </div>
                    <div>{render_status_badge(a.get('status', 'Scheduled'))}</div>
                </div>
                <div style="font-size: 0.825rem; color: #475569; margin-top: 0.25rem;">
                    <strong>Slot:</strong> {a.get('appointment_date')} at {str(a.get('time_slot'))[:5]} | <strong>Reason:</strong> {a.get('reason', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active appointments recorded.")
    
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("""
    <div class="glass-card" style="border: 1.5px solid #e9d5ff; background: #ffffff;">
        <div class="glass-card-header" style="color: #9333ea;">
            <span>✨ AI Rapid Symptom Intake</span>
            <span class="ai-badge">Instant Triage</span>
        </div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">
            Enter chief complaints to run immediate differential diagnosis and test recommendation.
        </div>
    """, unsafe_allow_html=True)

    quick_symptom = st.text_area(
        "Patient Chief Complaint / Symptoms",
        placeholder="e.g. 52-year-old reporting retrosternal squeezing chest pain on exertion, sweating and palpitations...",
        height=85,
        label_visibility="collapsed"
    )

    if st.button("Analyze with Clinical AI", type="primary", use_container_width=True):
        if quick_symptom.strip():
            with st.spinner("AI evaluating clinical presentation..."):
                analysis = ai_engine.analyze_symptoms(quick_symptom)
                st.success(f"**Likely Match:** {analysis['top_condition']} (ICD: `{analysis['icd_code']}`)")
                st.markdown(f"**Priority:** {analysis['triage']}")
                st.markdown(f"**Recommended Labs:** `{'`, `'.join(analysis['recommended_tests'][:3])}`")
                with st.expander("View Auto-Generated SOAP Note"):
                    st.markdown(f"<div class='soap-box'>{analysis['soap_note']}</div>", unsafe_allow_html=True)
        else:
            st.warning("Please type patient symptoms above.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SYSTEM HEALTH & AUDIT ACTIVITY
# ------------------------------------------------------------------------------
st.markdown("### 🔔 Recent System & Access Logs")
logs = client.list_access_logs()
if logs:
    log_df = pd.DataFrame(logs)
    log_df = log_df[["log_id", "action_type", "patient_id", "user_id", "remarks", "action_time"]]
    st.dataframe(log_df, use_container_width=True, hide_index=True)
else:
    st.caption("No system access logs recorded yet.")

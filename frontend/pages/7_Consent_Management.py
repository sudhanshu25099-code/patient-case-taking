"""
Consent Management & Data Governance Gateway
Ensures patient privacy, Doctor access authorizations, consent revocation, and comprehensive audit logs.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge

st.set_page_config(page_title="Consent Management • HealthPulse", page_icon="🛡️", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="Consent Management & Privacy Gateway",
    subtitle="Patient Data Authorization, Granular Physician Access Grants, Revocation & HIPAA Audit Trail",
    badge_text="Module 7",
    icon="🛡️"
)

tabs = st.tabs(["🛡️ Patient Consents", "🔑 Doctor Access Grants", "✅ Verify Access Rights", "📜 Audit Logs & Trail"])

# ------------------------------------------------------------------------------
# TAB 1: PATIENT CONSENTS
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 🛡️ Active & Historical Patient Consents")
    
    col_c_list, col_c_add = st.columns([1.6, 1.2])

    with col_c_list:
        consents = client.mock_db["consents"]
        for c in consents:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.15rem; margin-bottom: 0.85rem; border-left: 4px solid {'#10b981' if c.get('status') == 'Active' else '#ef4444'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">Consent #{c.get('consent_id')} — {c.get('patient_name')}</span>
                    {render_status_badge(c.get('status', 'Active'))}
                </div>
                <div style="font-size: 0.85rem; color: #334155; margin-top: 0.35rem;">
                    <strong>Purpose:</strong> {c.get('purpose', 'General clinical evaluation')}
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">
                    <strong>Validity:</strong> {c.get('valid_from','')[:10]} to {c.get('valid_to','')[:10]} | <strong>Type:</strong> {c.get('consent_type', 'View Only')}
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.2rem;">
                    Remarks: {c.get('remarks', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if c.get("status") == "Active":
                if st.button(f"Revoke Consent #{c['consent_id']}", key=f"rev_{c['consent_id']}", type="secondary"):
                    client.revoke_consent(c["consent_id"])
                    st.warning(f"Consent #{c['consent_id']} revoked immediately!")
                    st.rerun()

    with col_c_add:
        with st.expander("➕ Authorize New Patient Consent", expanded=True):
            with st.form("new_consent_form"):
                patients = client.list_patients()
                pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']})" for p in patients}
                c_patient = st.selectbox("Granting Patient", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

                hospitals = client.list_hospitals()
                hosp_opts = {h["hospital_id"]: h["name"] for h in hospitals}
                c_hospital = st.selectbox("Facility Scope", options=list(hosp_opts.keys()), format_func=lambda x: hosp_opts.get(x))

                purpose = st.text_input("Authorization Purpose", placeholder="e.g. Cardiology review, second opinion, lab disclosure")
                valid_days = st.number_input("Validity Duration (Days)", min_value=1, max_value=365, value=30)
                remarks = st.text_area("Specific Consent Restrictions / Remarks", placeholder="e.g. Permitted for diagnostic reports and consultation notes only.")

                if st.form_submit_button("Grant & Sign Consent", type="primary", use_container_width=True):
                    if purpose:
                        v_from = datetime.now()
                        client.create_consent({
                            "patient_id": c_patient,
                            "hospital_id": c_hospital,
                            "consent_type": "View Only",
                            "valid_from": v_from.isoformat(),
                            "valid_to": datetime.fromtimestamp(v_from.timestamp() + valid_days * 86400).isoformat(),
                            "status": "Active",
                            "purpose": purpose,
                            "remarks": remarks
                        })
                        st.success("Consent successfully granted and logged!")
                        st.rerun()
                    else:
                        st.error("Please enter the consent purpose.")

# ------------------------------------------------------------------------------
# TAB 2: DOCTOR ACCESS GRANTS
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 🔑 Doctor & Department Access Grants")
    
    col_ag_list, col_ag_add = st.columns([1.5, 1.3])

    with col_ag_list:
        st.markdown("#### Granted Access Authorizations")
        grants = client.mock_db["consent_access"]
        for g in grants:
            doc_name = g.get("doctor_name", f"Doctor #{g.get('doctor_id')}")
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between;">
                    <strong style="color: #0284c7;">{doc_name}</strong>
                    {render_status_badge(g.get('status', 'Active'))}
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-top: 0.25rem;">
                    <strong>Under Consent:</strong> #{g.get('consent_id')} | <strong>Department ID:</strong> #{g.get('department_id', 'All')}
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.2rem;">
                    Access Period: {g.get('access_from','')[:10]} to {g.get('access_to','')[:10]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_ag_add:
        with st.expander("➕ Grant Access to Physician", expanded=True):
            with st.form("grant_access_form"):
                active_consents = [c for c in client.mock_db["consents"] if c.get("status") == "Active"]
                if active_consents:
                    c_opts = {c["consent_id"]: f"Consent #{c['consent_id']} ({c.get('patient_name')} - {c.get('purpose')})" for c in active_consents}
                    target_c = st.selectbox("Under Patient Consent", options=list(c_opts.keys()), format_func=lambda x: c_opts.get(x))

                    doctors = client.list_doctors()
                    doc_opts = {d["doctor_id"]: f"{d['full_name']} ({d['specialization']})" for d in doctors}
                    target_doc = st.selectbox("Authorized Doctor", options=list(doc_opts.keys()), format_func=lambda x: doc_opts.get(x))

                    if st.form_submit_button("Grant Physician Access", type="primary", use_container_width=True):
                        client.grant_consent_access({
                            "consent_id": target_c,
                            "doctor_id": target_doc,
                            "access_from": datetime.now().isoformat(),
                            "access_to": datetime.fromtimestamp(datetime.now().timestamp() + 30 * 86400).isoformat()
                        })
                        st.success(f"Access granted to {doc_opts[target_doc]}!")
                        st.rerun()
                else:
                    st.info("No active patient consents available. Please grant a consent first.")

# ------------------------------------------------------------------------------
# TAB 3: VERIFY ACCESS RIGHTS
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### ✅ Immediate Access Authorization Check")
    st.caption("Verifies whether a physician has valid, active consent to access a patient's protected health records.")

    patients = client.list_patients()
    pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']})" for p in patients}
    chk_patient = st.selectbox("Select Patient Profile", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x), key="chk_p")

    doctors = client.list_doctors()
    doc_opts = {d["doctor_id"]: f"{d['full_name']} ({d['specialization']})" for d in doctors}
    chk_doctor = st.selectbox("Select Requesting Doctor", options=list(doc_opts.keys()), format_func=lambda x: doc_opts.get(x), key="chk_d")

    if st.button("Check Access Permissions", type="primary", use_container_width=True):
        res = client.check_doctor_access(chk_patient, chk_doctor)
        if res.get("has_access"):
            st.markdown(f"""
            <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 12px; padding: 1.5rem; margin-top: 1rem;">
                <div style="font-size: 1.25rem; font-weight: 800; color: #15803d;">
                    ✅ ACCESS PERMITTED
                </div>
                <div style="font-size: 0.95rem; color: #166534; margin-top: 0.5rem;">
                    <strong>{doc_opts[chk_doctor]}</strong> is authorized to view protected records for <strong>{pat_opts[chk_patient]}</strong>.
                </div>
                <div style="font-size: 0.85rem; color: #14532d; margin-top: 0.35rem;">
                    Under Consent ID: <strong>#{res.get('consent_id')}</strong> | Purpose: <em>"{res.get('purpose')}"</em>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #fef2f2; border: 2px solid #fca5a5; border-radius: 12px; padding: 1.5rem; margin-top: 1rem;">
                <div style="font-size: 1.25rem; font-weight: 800; color: #b91c1c;">
                    ⛔ ACCESS DENIED / NO ACTIVE CONSENT
                </div>
                <div style="font-size: 0.95rem; color: #991b1b; margin-top: 0.5rem;">
                    <strong>{doc_opts[chk_doctor]}</strong> does not hold active patient consent for <strong>{pat_opts[chk_patient]}</strong>.
                </div>
                <div style="font-size: 0.85rem; color: #7f1d1d; margin-top: 0.35rem;">
                    To view this patient's case sheet or documents, obtain authorization in the 'Patient Consents' tab.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 4: AUDIT LOGS & TRAIL
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 📜 System Access Logs & Audit Trail")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("#### Patient Record Access Logs")
        access_logs = client.list_access_logs()
        if access_logs:
            st.dataframe(pd.DataFrame(access_logs), use_container_width=True, hide_index=True)
        else:
            st.caption("No access logs recorded.")

    with col_l2:
        st.markdown("#### System Database Audit Trail")
        audit_trail = client.list_audit_trail()
        if audit_trail:
            st.dataframe(pd.DataFrame(audit_trail), use_container_width=True, hide_index=True)
        else:
            st.caption("No audit entries.")

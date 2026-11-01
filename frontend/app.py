import streamlit as st
from utils.ui_helpers import apply_theme, render_role_badge
from views.auth_view import render_login_view

from views.doctor_views import (
    doctor_station_view, doctor_case_taking_view, doctor_diagnostics_view,
    doctor_patient_records_view, doctor_ai_assistant_view
)
from views.nurse_views import (
    nurse_station_view, nurse_checkin_view, nurse_care_view,
    nurse_labs_view, nurse_directory_view
)
from views.patient_views import (
    patient_overview_view, patient_appointments_view, patient_medical_records_view,
    patient_lab_reports_view, patient_documents_view, patient_consent_view
)
from views.admin_views import (
    admin_overview_view, admin_hospitals_view, admin_users_view,
    admin_appointments_view, admin_clinical_view, admin_diagnostics_view,
    admin_documents_view, admin_consent_view, admin_audit_view,
    admin_ai_assistant_view
)

st.set_page_config(
    page_title="Clinical EHR",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# Check authentication
if "username" not in st.session_state or not st.session_state.get("user_info"):
    render_login_view()
else:
    user_info = st.session_state["user_info"]
    primary_role = user_info.get("primary_role", "Patient")

    # Sidebar Header & User Profile
    with st.sidebar:
        st.markdown(f"### 🏥 HealthPulse EHR")
        st.markdown(f"**{user_info.get('full_name')}**")
        st.markdown(f"`@{user_info.get('username')}`")
        st.markdown(render_role_badge(primary_role), unsafe_allow_html=True)
        st.markdown("---")

        active_role = primary_role

        # Admin View Switcher (Allows admin to view the portal from any role perspective)
        if primary_role == "Admin":
            st.markdown("👑 **Admin Perspective Control**")
            simulated = st.selectbox(
                "Active Viewing Mode",
                ["Admin (Whole Access)", "Doctor View", "Nurse View", "Patient View"],
                index=0,
                key="admin_perspective"
            )
            if "Doctor" in simulated:
                active_role = "Doctor"
            elif "Nurse" in simulated:
                active_role = "Nurse"
            elif "Patient" in simulated:
                active_role = "Patient"
            else:
                active_role = "Admin"
            st.markdown("---")

        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

    # Route navigation according to active role
    if active_role == "Doctor":
        pages = {
            "Doctor Portal": [
                st.Page(doctor_station_view, title="Doctor Station & Queue", icon="🩺", default=True),
                st.Page(doctor_case_taking_view, title="Clinical Case Taking", icon="📋"),
                st.Page(doctor_diagnostics_view, title="Lab & Diagnostics", icon="🔬"),
                st.Page(doctor_patient_records_view, title="Patient EMR Vault", icon="📂"),
                st.Page(doctor_ai_assistant_view, title="AI Clinical Assistant", icon="🧠"),
            ]
        }
    elif active_role == "Nurse":
        pages = {
            "Nurse Station": [
                st.Page(nurse_station_view, title="Clinic Triage Queue", icon="👩‍⚕️", default=True),
                st.Page(nurse_checkin_view, title="Check-In & Vitals Intake", icon="⏱️"),
                st.Page(nurse_care_view, title="Allergies & Care Records", icon="💊"),
                st.Page(nurse_labs_view, title="Lab Orders Tracking", icon="🧪"),
                st.Page(nurse_directory_view, title="Patient Directory", icon="📇"),
            ]
        }
    elif active_role == "Patient":
        pages = {
            "Patient Portal": [
                st.Page(patient_overview_view, title="My Health Profile", icon="👤", default=True),
                st.Page(patient_appointments_view, title="My Appointments", icon="📅"),
                st.Page(patient_medical_records_view, title="My Medical Records", icon="💊"),
                st.Page(patient_lab_reports_view, title="My Diagnostic Reports", icon="🔬"),
                st.Page(patient_documents_view, title="My Health Documents", icon="📁"),
                st.Page(patient_consent_view, title="Consent & Privacy", icon="🔏"),
            ]
        }
    else:  # Admin (Whole Access)
        pages = {
            "Administration": [
                st.Page(admin_overview_view, title="Executive Overview", icon="📊", default=True),
                st.Page(admin_hospitals_view, title="Hospital Administration", icon="🏥"),
                st.Page(admin_users_view, title="User & Identity Hub", icon="👥"),
                st.Page(admin_appointments_view, title="Master Appointments", icon="📅"),
            ],
            "Clinical Vault": [
                st.Page(admin_clinical_view, title="Clinical Records & EMR", icon="🩺"),
                st.Page(admin_diagnostics_view, title="Diagnostics Catalog", icon="🔬"),
                st.Page(admin_documents_view, title="Document Vault", icon="📁"),
            ],
            "Security & Intelligence": [
                st.Page(admin_consent_view, title="Consent Oversight", icon="🔏"),
                st.Page(admin_audit_view, title="Security & Audit Logs", icon="📜"),
                st.Page(admin_ai_assistant_view, title="AI Assistant", icon="🧠"),
            ]
        }

    nav = st.navigation(pages)
    nav.run()

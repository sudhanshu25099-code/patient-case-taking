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
    page_icon=":material/local_hospital:",
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
        st.markdown("""
            <div class="hp-sidebar-brand">
                <div class="hp-brand-mark">+</div>
                <div>
                    <div class="hp-brand-name">Clinical EHR</div>
                    <div class="hp-brand-sub">Connected care workspace</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="hp-user-panel">
                <div class="hp-user-name">{user_info.get('full_name')}</div>
                <div class="hp-user-handle">@{user_info.get('username')}</div>
                {render_role_badge(primary_role)}
            </div>
        """, unsafe_allow_html=True)

        active_role = primary_role

        # Admin View Switcher (Allows admin to view the portal from any role perspective)
        if primary_role == "Admin":
            st.markdown(":material/admin_panel_settings: **Admin Perspective Control**")
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

        if st.button(":material/logout: Sign Out", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

    # Route navigation according to active role
    if active_role == "Doctor":
        pages = {
            "Doctor Portal": [
                st.Page(doctor_station_view, title="Doctor Station & Queue", icon=":material/stethoscope:", default=True),
                st.Page(doctor_case_taking_view, title="Clinical Case Taking", icon=":material/assignment:"),
                st.Page(doctor_diagnostics_view, title="Lab & Diagnostics", icon=":material/labs:"),
                st.Page(doctor_patient_records_view, title="Patient EMR Vault", icon=":material/folder_open:"),
                st.Page(doctor_ai_assistant_view, title="AI Clinical Assistant", icon=":material/neurology:"),
            ]
        }
    elif active_role == "Nurse":
        pages = {
            "Nurse Station": [
                st.Page(nurse_station_view, title="Clinic Triage Queue", icon=":material/medical_services:", default=True),
                st.Page(nurse_checkin_view, title="Check-In & Vitals Intake", icon=":material/timer:"),
                st.Page(nurse_care_view, title="Allergies & Care Records", icon=":material/medication:"),
                st.Page(nurse_labs_view, title="Lab Orders Tracking", icon=":material/experiment:"),
                st.Page(nurse_directory_view, title="Patient Directory", icon=":material/contacts:"),
            ]
        }
    elif active_role == "Patient":
        pages = {
            "Patient Portal": [
                st.Page(patient_overview_view, title="My Health Profile", icon=":material/person:", default=True),
                st.Page(patient_appointments_view, title="My Appointments", icon=":material/calendar_month:"),
                st.Page(patient_medical_records_view, title="My Medical Records", icon=":material/medication:"),
                st.Page(patient_lab_reports_view, title="My Diagnostic Reports", icon=":material/labs:"),
                st.Page(patient_documents_view, title="My Health Documents", icon=":material/folder:"),
                st.Page(patient_consent_view, title="Consent & Privacy", icon=":material/policy:"),
            ]
        }
    else:  # Admin (Whole Access)
        pages = {
            "Administration": [
                st.Page(admin_overview_view, title="Executive Overview", icon=":material/monitoring:", default=True),
                st.Page(admin_hospitals_view, title="Hospital Administration", icon=":material/local_hospital:"),
                st.Page(admin_users_view, title="User & Identity Hub", icon=":material/groups:"),
                st.Page(admin_appointments_view, title="Master Appointments", icon=":material/calendar_month:"),
            ],
            "Clinical Vault": [
                st.Page(admin_clinical_view, title="Clinical Records & EMR", icon=":material/stethoscope:"),
                st.Page(admin_diagnostics_view, title="Diagnostics Catalog", icon=":material/labs:"),
                st.Page(admin_documents_view, title="Document Vault", icon=":material/folder:"),
            ],
            "Security & Intelligence": [
                st.Page(admin_consent_view, title="Consent Oversight", icon=":material/policy:"),
                st.Page(admin_audit_view, title="Security & Audit Logs", icon=":material/receipt_long:"),
                st.Page(admin_ai_assistant_view, title="AI Assistant", icon=":material/neurology:"),
            ]
        }

    nav = st.navigation(pages)
    nav.run()

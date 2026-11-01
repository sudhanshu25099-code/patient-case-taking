"""
UI Helper functions and styling for Patient Case Taking & Record System.
Provides clinical-grade aesthetics, responsive components, status badges,
and cohesive state management across all Streamlit pages.
"""

import streamlit as st
from typing import Optional, Dict, Any


def inject_custom_css():
    """Injects high-end, responsive clinical CSS for a modern healthcare application."""
    st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall Background & Canvas */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Top Header Banner */
    .clinical-banner {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 50%, #1d4ed8 100%);
        padding: 1.75rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .clinical-banner h1 {
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.025em;
        color: #ffffff;
    }
    .clinical-banner p {
        font-size: 0.95rem;
        margin: 0.35rem 0 0 0;
        opacity: 0.92;
        color: #e0f2fe;
    }
    .clinical-banner-badge {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 0.4rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* KPI / Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -8px rgba(15, 23, 42, 0.08);
    }
    .metric-card-title {
        font-size: 0.825rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.4rem;
    }
    .metric-card-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-card-sub {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 600;
        margin-top: 0.3rem;
    }

    /* Section Cards */
    .glass-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.04);
    }
    .glass-card-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 0.75rem;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-scheduled { background-color: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
    .badge-completed { background-color: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-cancelled { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
    .badge-inprogress { background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
    .badge-active { background-color: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }
    .badge-high { background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }
    .badge-normal { background-color: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
    .badge-low { background-color: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }

    /* Custom Streamlit component overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0284c7 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
    }

    /* Sidebar Cleanliness */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Code/SOAP Note Container */
    .soap-box {
        background-color: #f8fafc;
        border-left: 4px solid #0284c7;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #334155;
        white-space: pre-wrap;
    }

    /* AI Insight Pill */
    .ai-badge {
        background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
        color: white;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, badge_text: str = "Clinical Portal v2.0", icon: str = "🏥"):
    """Renders the sleek, branded header banner at the top of pages."""
    st.markdown(f"""
    <div class="clinical-banner">
        <div>
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        <div class="clinical-banner-badge">{badge_text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: Any, sub: str = "", icon: str = "📈"):
    """Renders a styled metric KPI box."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">{icon} {title}</div>
        <div class="metric-card-value">{value}</div>
        {f'<div class="metric-card-sub">{sub}</div>' if sub else ''}
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Returns HTML for an authentic, color-coded pill badge."""
    s_lower = str(status).lower().replace(" ", "")
    cls_map = {
        "scheduled": "badge-scheduled",
        "completed": "badge-completed",
        "cancelled": "badge-cancelled",
        "noshow": "badge-cancelled",
        "inprogress": "badge-inprogress",
        "active": "badge-active",
        "controlled": "badge-completed",
        "resolved": "badge-normal",
        "high": "badge-high",
        "normal": "badge-normal",
        "low": "badge-low",
        "verified": "badge-completed",
        "pending": "badge-inprogress",
        "rejected": "badge-cancelled"
    }
    cls = cls_map.get(s_lower, "badge-scheduled")
    return f'<span class="badge {cls}">{status}</span>'


def render_sidebar_context(client):
    """Renders the active session user, role switcher, and backend status in the sidebar."""
    with st.sidebar:
        st.markdown("### 🏥 Active Context")
        
        # User Role Selection
        roles = ["Doctor", "Super Admin", "Hospital Admin", "Nurse", "Patient"]
        if "user_role" not in st.session_state:
            st.session_state["user_role"] = "Doctor"
        selected_role = st.selectbox("Current Role", roles, index=roles.index(st.session_state["user_role"]))
        st.session_state["user_role"] = selected_role

        # Active Doctor / Patient selector based on role
        if selected_role in ("Doctor", "Hospital Admin"):
            doctors = client.list_doctors()
            doc_options = {d["doctor_id"]: f"{d['full_name']} ({d['specialization']})" for d in doctors}
            if "active_doctor_id" not in st.session_state:
                st.session_state["active_doctor_id"] = doctors[0]["doctor_id"] if doctors else 1
            cur_doc = st.selectbox(
                "Logged-in Physician",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options.get(x, f"Doctor #{x}")
            )
            st.session_state["active_doctor_id"] = cur_doc

        elif selected_role == "Patient":
            patients = client.list_patients()
            pat_options = {p["patient_id"]: f"{p['full_name']} [{p.get('blood_group','')}]" for p in patients}
            if "active_patient_id" not in st.session_state:
                st.session_state["active_patient_id"] = patients[0]["patient_id"] if patients else 1
            cur_pat = st.selectbox(
                "Active Patient Profile",
                options=list(pat_options.keys()),
                format_func=lambda x: pat_options.get(x, f"Patient #{x}")
            )
            st.session_state["active_patient_id"] = cur_pat

        # Active Hospital
        hospitals = client.list_hospitals()
        hosp_options = {h["hospital_id"]: h["name"] for h in hospitals}
        if "active_hospital_id" not in st.session_state:
            st.session_state["active_hospital_id"] = hospitals[0]["hospital_id"] if hospitals else 1
        cur_hosp = st.selectbox(
            "Facility / Hospital",
            options=list(hosp_options.keys()),
            format_func=lambda x: hosp_options.get(x, f"Hospital #{x}")
        )
        st.session_state["active_hospital_id"] = cur_hosp

        st.markdown("---")
        
        # Backend Connectivity Status
        health = client.check_health()
        if health["online"]:
            st.markdown(f"🟢 **FastAPI Live** (`{health['url']}`)")
        else:
            st.markdown("🟡 **Resilient Demo Mode** (In-Memory)")
            with st.expander("API Server Config"):
                custom_url = st.text_input("Backend URL", value=client.base_url)
                if st.button("Reconnect API"):
                    client.base_url = custom_url
                    st.rerun()

        st.caption("Patient Case Taking & EHR System • MySQL/FastAPI")

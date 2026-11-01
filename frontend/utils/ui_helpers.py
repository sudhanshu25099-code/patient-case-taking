import streamlit as st


def apply_theme():
    """Injects custom CSS for modern healthcare EHR portal."""
    st.markdown("""
        <style>
        /* Base typography & backgrounds */
        .stApp {
            background-color: #F8FAFC;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        
        [data-testid="stSidebar"] * {
            color: #1E293B !important;
        }
        
        /* Metric Cards */
        .hp-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 18px 20px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 16px;
        }
        .hp-card-title {
            font-size: 0.85rem;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .hp-card-val {
            font-size: 1.85rem;
            font-weight: 700;
            color: #0F172A;
            margin: 4px 0;
        }
        .hp-card-sub {
            font-size: 0.8rem;
            color: #94A3B8;
        }
        
        /* Badges */
        .hp-badge {
            display: inline-block;
            padding: 3px 10px;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 9999px;
            margin-right: 6px;
        }
        .hp-badge-doctor { background: #DBEAFE; color: #1E40AF; }
        .hp-badge-nurse { background: #E0E7FF; color: #3730A3; }
        .hp-badge-patient { background: #DCFCE7; color: #166534; }
        .hp-badge-admin { background: #FEE2E2; color: #991B1B; }
        .hp-badge-active { background: #DCFCE7; color: #15803D; }
        .hp-badge-scheduled { background: #EFF6FF; color: #2563EB; }
        .hp-badge-completed { background: #F1F5F9; color: #475569; }
        .hp-badge-warning { background: #FEF3C7; color: #92400E; }
        
        /* Header Box */
        .hp-header-box {
            background: linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%);
            border-radius: 12px;
            padding: 20px 24px;
            border: 1px solid #E2E8F0;
            margin-bottom: 24px;
        }
        </style>
    """, unsafe_allow_html=True)


def page_header(title, icon="🏥", description=""):
    st.markdown(f"""
        <div class="hp-header-box">
            <h1 style="margin: 0; font-size: 1.75rem; color: #0F172A; display: flex; align-items: center; gap: 10px;">
                <span>{icon}</span> <span>{title}</span>
            </h1>
            {f'<p style="margin: 6px 0 0 0; color: #64748B; font-size: 0.95rem;">{description}</p>' if description else ''}
        </div>
    """, unsafe_allow_html=True)


def render_kpi_card(title, value, subtitle="", icon="📌"):
    st.markdown(f"""
        <div class="hp-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="hp-card-title">{title}</span>
                <span style="font-size: 1.25rem;">{icon}</span>
            </div>
            <div class="hp-card-val">{value}</div>
            {f'<div class="hp-card-sub">{subtitle}</div>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)


def render_role_badge(role: str):
    r_lower = role.lower()
    if "admin" in r_lower:
        cls = "hp-badge-admin"
    elif "doctor" in r_lower:
        cls = "hp-badge-doctor"
    elif "nurse" in r_lower:
        cls = "hp-badge-nurse"
    else:
        cls = "hp-badge-patient"
    return f'<span class="hp-badge {cls}">{role}</span>'


def render_status_badge(status: str):
    s = (status or "").lower()
    if s in ["active", "completed", "verified"]:
        cls = "hp-badge-active"
    elif s in ["scheduled", "pending"]:
        cls = "hp-badge-scheduled"
    elif s in ["cancelled", "rejected"]:
        cls = "hp-badge-admin"
    else:
        cls = "hp-badge-warning"
    return f'<span class="hp-badge {cls}">{status}</span>'


def check_login():
    if "username" not in st.session_state or not st.session_state.get("user_info"):
        st.warning("⚠️ Please log in first.")
        st.stop()

import streamlit as st


def apply_theme():
    """Inject the shared visual system for the clinical workspace."""
    st.markdown("""
        <style>
        :root {
            --hp-ink: #102A43;
            --hp-muted: #627D98;
            --hp-faint: #829AB1;
            --hp-line: #D9E2EC;
            --hp-surface: #FFFFFF;
            --hp-canvas: #F4F7FA;
            --hp-primary: #0F766E;
            --hp-primary-dark: #115E59;
            --hp-primary-soft: #E6FFFA;
            --hp-accent: #2563EB;
            --hp-danger: #B42318;
            --hp-warning: #B54708;
            --hp-radius: 14px;
            --hp-shadow: 0 8px 24px rgba(16, 42, 67, 0.06);
        }

        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", sans-serif;
        }

        .stApp {
            color: var(--hp-ink);
            background:
                radial-gradient(circle at 88% 0%, rgba(15, 118, 110, 0.06), transparent 28rem),
                var(--hp-canvas);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
            border-right: 1px solid var(--hp-line);
            box-shadow: 8px 0 30px rgba(16, 42, 67, 0.035);
        }
        
        [data-testid="stSidebar"] * {
            color: var(--hp-ink);
        }

        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding: 1.2rem 0.8rem;
        }

        [data-testid="stSidebarNav"] span {
            font-weight: 600;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 10px;
            margin: 0.15rem 0;
            transition: background 160ms ease, transform 160ms ease;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: var(--hp-primary-soft);
            transform: translateX(2px);
        }

        .hp-sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.25rem 0 1rem;
            border-bottom: 1px solid var(--hp-line);
            margin-bottom: 1rem;
        }

        .hp-brand-mark {
            display: grid;
            place-items: center;
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 12px;
            color: #FFFFFF !important;
            background: linear-gradient(135deg, var(--hp-primary), #0891B2);
            box-shadow: 0 8px 18px rgba(15, 118, 110, 0.2);
            font-weight: 800;
        }

        .hp-brand-name {
            color: var(--hp-ink);
            font-size: 1rem;
            font-weight: 750;
            line-height: 1.2;
        }

        .hp-brand-sub {
            color: var(--hp-muted);
            font-size: 0.72rem;
            margin-top: 0.15rem;
        }

        .hp-user-panel {
            padding: 0.85rem 0.9rem;
            border: 1px solid var(--hp-line);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.8);
            margin-bottom: 0.5rem;
        }

        .hp-user-name {
            color: var(--hp-ink);
            font-weight: 700;
            line-height: 1.25;
        }

        .hp-user-handle {
            color: var(--hp-muted);
            font-size: 0.78rem;
            margin: 0.15rem 0 0.55rem;
        }
        
        .hp-card {
            position: relative;
            min-height: 8.2rem;
            overflow: hidden;
            background: var(--hp-surface);
            border-radius: var(--hp-radius);
            padding: 1.15rem 1.2rem;
            border: 1px solid var(--hp-line);
            box-shadow: 0 3px 12px rgba(16, 42, 67, 0.04);
            margin-bottom: 1rem;
            transition: transform 160ms ease, box-shadow 160ms ease;
        }

        .hp-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 3px;
            background: linear-gradient(180deg, var(--hp-primary), #22C55E);
        }

        .hp-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--hp-shadow);
        }

        .hp-card-topline {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
        }

        .hp-card-icon {
            display: grid;
            place-items: center;
            width: 2rem;
            height: 2rem;
            border-radius: 9px;
            background: var(--hp-primary-soft);
            color: var(--hp-primary);
        }

        .material-symbols-rounded {
            font-family: "Material Symbols Rounded";
            font-weight: normal;
            font-style: normal;
            font-size: 1.25rem;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-feature-settings: "liga";
            -webkit-font-smoothing: antialiased;
            font-feature-settings: "liga";
            vertical-align: -0.2em;
        }

        .hp-header-icon {
            display: grid;
            place-items: center;
            width: 2.4rem;
            height: 2.4rem;
            flex: 0 0 auto;
            border-radius: 11px;
            color: var(--hp-primary);
            background: var(--hp-primary-soft);
        }

        .hp-card-title {
            font-size: 0.72rem;
            color: var(--hp-muted);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.065em;
        }

        .hp-card-val {
            font-size: clamp(1.5rem, 2vw, 2rem);
            font-weight: 750;
            color: var(--hp-ink);
            letter-spacing: -0.035em;
            margin: 0.45rem 0 0.2rem;
        }

        .hp-card-sub {
            font-size: 0.78rem;
            color: var(--hp-faint);
        }
        
        .hp-badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            font-size: 0.7rem;
            font-weight: 700;
            border-radius: 999px;
            margin-right: 0.35rem;
            letter-spacing: 0.015em;
        }

        .hp-badge-doctor { background: #E0F2FE; color: #075985; }
        .hp-badge-nurse { background: #EDE9FE; color: #5B21B6; }
        .hp-badge-patient { background: #DCFCE7; color: #166534; }
        .hp-badge-admin { background: #FEE2E2; color: #991B1B; }
        .hp-badge-active { background: #DCFCE7; color: #166534; }
        .hp-badge-scheduled { background: #DBEAFE; color: #1D4ED8; }
        .hp-badge-completed { background: #E2E8F0; color: #334155; }
        .hp-badge-warning { background: #FEF3C7; color: #92400E; }
        
        .hp-header-box {
            position: relative;
            overflow: hidden;
            background: linear-gradient(125deg, #FFFFFF 0%, #F0FDFA 100%);
            border-radius: 18px;
            padding: 1.35rem 1.5rem;
            border: 1px solid #CFE8E5;
            box-shadow: var(--hp-shadow);
            margin-bottom: 1.5rem;
        }

        .hp-header-box::after {
            content: "";
            position: absolute;
            width: 11rem;
            height: 11rem;
            right: -4rem;
            top: -6rem;
            border-radius: 50%;
            background: rgba(15, 118, 110, 0.075);
        }

        .hp-header-eyebrow {
            color: var(--hp-primary);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .hp-header-title {
            position: relative;
            z-index: 1;
            margin: 0;
            color: var(--hp-ink);
            display: flex;
            align-items: center;
            gap: 0.7rem;
            font-size: clamp(1.45rem, 2vw, 1.9rem);
            letter-spacing: -0.035em;
            line-height: 1.2;
        }

        .hp-header-description {
            position: relative;
            z-index: 1;
            max-width: 54rem;
            margin: 0.5rem 0 0;
            color: var(--hp-muted);
            font-size: 0.92rem;
        }

        .hp-login-hero {
            max-width: 48rem;
            margin: 1.5rem auto 2rem;
            text-align: center;
        }

        .hp-login-mark {
            display: grid;
            place-items: center;
            width: 4.25rem;
            height: 4.25rem;
            margin: 0 auto 1rem;
            border-radius: 20px;
            color: #FFFFFF;
            background: linear-gradient(135deg, var(--hp-primary), #0891B2);
            box-shadow: 0 16px 32px rgba(15, 118, 110, 0.22);
            font-size: 2rem;
        }

        .hp-login-title {
            margin: 0;
            color: var(--hp-ink);
            font-size: clamp(2rem, 4vw, 2.8rem);
            letter-spacing: -0.055em;
        }

        .hp-login-subtitle {
            max-width: 40rem;
            margin: 0.65rem auto 0;
            color: var(--hp-muted);
            line-height: 1.65;
        }

        div[data-testid="stForm"] {
            padding: 1.25rem;
            border: 1px solid var(--hp-line);
            border-radius: var(--hp-radius);
            background: rgba(255, 255, 255, 0.82);
            box-shadow: 0 4px 16px rgba(16, 42, 67, 0.035);
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            border-color: var(--hp-line);
            border-radius: 10px;
            background: #FFFFFF;
        }

        div[data-baseweb="input"]:focus-within > div,
        div[data-baseweb="select"]:focus-within > div,
        div[data-baseweb="textarea"]:focus-within > div {
            border-color: var(--hp-primary);
            box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.1);
        }

        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {
            min-height: 2.55rem;
            border-radius: 10px;
            border-color: var(--hp-line);
            font-weight: 700;
            transition: transform 140ms ease, box-shadow 140ms ease;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            border-color: var(--hp-primary);
            box-shadow: 0 6px 16px rgba(15, 118, 110, 0.12);
        }

        button[kind="primary"],
        .stFormSubmitButton button[kind="primary"] {
            color: #FFFFFF;
            background: linear-gradient(135deg, var(--hp-primary), var(--hp-primary-dark));
            border-color: var(--hp-primary);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.3rem;
            padding: 0.25rem;
            border-radius: 12px;
            background: #EAF0F5;
        }

        .stTabs [data-baseweb="tab"] {
            height: 2.65rem;
            padding: 0 0.9rem;
            border-radius: 9px;
            font-weight: 650;
        }

        .stTabs [aria-selected="true"] {
            background: #FFFFFF;
            box-shadow: 0 2px 8px rgba(16, 42, 67, 0.08);
        }

        [data-testid="stExpander"] {
            overflow: hidden;
            border: 1px solid var(--hp-line);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.86);
            box-shadow: 0 2px 8px rgba(16, 42, 67, 0.025);
        }

        [data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid var(--hp-line);
            border-radius: 12px;
            background: #FFFFFF;
        }

        [data-testid="stAlert"] {
            border-radius: 12px;
            border-width: 1px;
        }

        hr {
            margin: 1.5rem 0;
            border-color: var(--hp-line);
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem;
            }

            .hp-header-box {
                padding: 1.1rem;
                border-radius: 14px;
            }

            .hp-card {
                min-height: auto;
            }
        }
        </style>
    """, unsafe_allow_html=True)


def _material_icon_markup(icon: str, class_name: str = "") -> str:
    """Render Streamlit's Material Symbol token inside custom HTML components."""
    icon_name = str(icon).removeprefix(":material/").removesuffix(":")
    classes = f"material-symbols-rounded {class_name}".strip()
    return f'<span class="{classes}" aria-hidden="true">{icon_name}</span>'


def page_header(title, icon="local_hospital", description=""):
    st.markdown(f"""
        <div class="hp-header-box">
            <div class="hp-header-eyebrow">Clinical workspace</div>
            <div class="hp-header-title" role="heading" aria-level="1">
                <span class="hp-header-icon">{_material_icon_markup(icon)}</span>
                <span>{title}</span>
            </div>
            {f'<p class="hp-header-description">{description}</p>' if description else ''}
        </div>
    """, unsafe_allow_html=True)


def render_kpi_card(title, value, subtitle="", icon="push_pin"):
    st.markdown(f"""
        <div class="hp-card">
            <div class="hp-card-topline">
                <span class="hp-card-title">{title}</span>
                <span class="hp-card-icon">{_material_icon_markup(icon)}</span>
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
        st.warning(":material/warning: Please log in first.")
        st.stop()

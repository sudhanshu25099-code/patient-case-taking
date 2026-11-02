import streamlit as st
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, flash_success, flash_error, flash_warning


LOGIN_BACKGROUND_CSS = """
<style>
.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(15, 118, 110, 0.18), transparent 26rem),
        radial-gradient(circle at 90% 18%, rgba(8, 145, 178, 0.16), transparent 24rem),
        radial-gradient(circle at 70% 95%, rgba(37, 99, 235, 0.10), transparent 28rem),
        linear-gradient(160deg, #F0FDFA 0%, #F4F7FA 55%, #EAF3F8 100%);
    background-attachment: fixed;
}

/* Medical-cross grid */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.55;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='72' height='72' viewBox='0 0 72 72'%3E%3Cpath d='M36 29v14M29 36h14' stroke='%230F766E' stroke-opacity='0.16' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E");
    -webkit-mask-image: radial-gradient(ellipse at center, transparent 18%, #000 85%);
    mask-image: radial-gradient(ellipse at center, transparent 18%, #000 85%);
}

/* ECG pulse line along the lower edge */
.stApp::after {
    content: "";
    position: fixed;
    left: 0;
    right: 0;
    bottom: 6vh;
    height: 9rem;
    z-index: 0;
    pointer-events: none;
    opacity: 0.9;
    background-repeat: repeat-x;
    background-position: center;
    background-size: 56rem 100%;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='896' height='144' viewBox='0 0 896 144' fill='none'%3E%3Cpath d='M0 72h250l18-8 18 8h40l14 30 24-86 28 108 22-52h26l16-14 16 14h424' stroke='%230F766E' stroke-opacity='0.22' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 25%, #000 75%, transparent);
    mask-image: linear-gradient(90deg, transparent, #000 25%, #000 75%, transparent);
}

[data-testid="stMain"], [data-testid="stHeader"] { position: relative; z-index: 1; background: transparent; }

.hp-login-mark { position: relative; }
.hp-login-mark::after {
    content: "";
    position: absolute;
    inset: -0.7rem;
    border-radius: 26px;
    border: 1px solid rgba(15, 118, 110, 0.22);
}

@media (max-width: 768px) {
    .stApp::after { bottom: 2vh; background-size: 36rem 100%; }
}
</style>
"""


def render_login_view():
    apply_theme()
    st.markdown(LOGIN_BACKGROUND_CSS, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="hp-login-hero">
            <div class="hp-login-mark">+</div>
            <div class="hp-header-eyebrow">Secure clinical operations</div>
            <div class="hp-login-title" role="heading" aria-level="1">Clinical EHR</div>
            <p class="hp-login-subtitle">
                One connected workspace for care teams, patients, and hospital
                operations—with role-aware access to every clinical workflow.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        tab_login, tab_demo = st.tabs([":material/key: Sign In", ":material/rocket_launch: Quick Demo Switcher"])
        
        with tab_login:
            with st.form("standard_login"):
                st.subheader("Account Login")
                username = st.text_input("Username or Email", placeholder="e.g. dr.sharma, aarav.mehta, admin")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                
                if submit:
                    if not username.strip() or not password.strip():
                        flash_warning("Please enter both username and password.")
                    else:
                        st.session_state["username"] = username.strip()
                        st.session_state["password"] = password.strip()
                        
                        res = api_request("GET", "/auth/me")
                        if res is not None and res.status_code == 200:
                            st.session_state["user_info"] = res.json()
                            role = st.session_state["user_info"].get("primary_role", "User")
                            name = st.session_state["user_info"].get("full_name")
                            flash_success(f"Welcome back, {name}! Successfully authenticated as {role}.")
                            st.rerun()
                        else:
                            st.session_state.pop("username", None)
                            st.session_state.pop("password", None)
                            flash_error("Invalid username or password.")
                            
        with tab_demo:
            st.info(":material/bolt: Test any user persona with 1-click. Default password is **`password123`**.")
            
            c_adm, c_doc = st.columns(2)
            with c_adm:
                if st.button(":material/admin_panel_settings: Admin (Whole Access)\n`admin`", use_container_width=True):
                    _do_demo_login("admin")
            with c_doc:
                if st.button(":material/stethoscope: Doctor (Dr. Sharma)\n`dr.sharma`", use_container_width=True):
                    _do_demo_login("dr.sharma")
                    
            c_nur, c_pat = st.columns(2)
            with c_nur:
                if st.button(":material/medical_services: Nurse (Nurse Rao)\n`nurse.rao`", use_container_width=True):
                    _do_demo_login("nurse.rao")
            with c_pat:
                if st.button(":material/person: Patient (Aarav Mehta)\n`aarav.mehta`", use_container_width=True):
                    _do_demo_login("aarav.mehta")


def _do_demo_login(username: str):
    st.session_state["username"] = username
    st.session_state["password"] = "password123"
    res = api_request("GET", "/auth/me")
    if res is not None and res.status_code == 200:
        st.session_state["user_info"] = res.json()
        role = st.session_state["user_info"].get("primary_role", "User")
        flash_success(f"Signed in as @{username} ({role})")
        st.rerun()
    else:
        st.session_state.pop("username", None)
        st.session_state.pop("password", None)
        flash_error(f"Failed to authenticate demo user @{username}")

import streamlit as st
from utils.api_client import api_request
from utils.ui_helpers import apply_theme


def render_login_view():
    apply_theme()
    
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
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        st.session_state["username"] = username.strip()
                        st.session_state["password"] = password.strip()
                        
                        res = api_request("GET", "/auth/me")
                        if res is not None and res.status_code == 200:
                            st.session_state["user_info"] = res.json()
                            st.success(f"Welcome back, {st.session_state['user_info'].get('full_name')}!")
                            st.rerun()
                        else:
                            st.session_state.pop("username", None)
                            st.session_state.pop("password", None)
                            st.error("Invalid username or password.")
                            
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
        st.rerun()
    else:
        st.error(f"Failed to authenticate demo user: {username}")
 
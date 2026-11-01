import streamlit as st
from utils.api_client import api_request
from utils.ui_helpers import apply_theme


def render_login_view():
    apply_theme()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 3rem;">🏥</span>
            <h1 style="color: #0F172A; margin: 4px 0;">Clinical EHR</h1>
            <p style="color: #64748B; font-size: 1.05rem;">
                Unified Role-Based Access for Doctors, Nurses, Patients & Hospital Administration
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("""
            <div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        """, unsafe_allow_html=True)
        
        tab_login, tab_demo = st.tabs(["🔑 Sign In", "🚀 Quick Demo Switcher"])
        
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
            st.info("⚡ Test any user persona with 1-click. Default password is **`password123`**.")
            
            c_adm, c_doc = st.columns(2)
            with c_adm:
                if st.button("👑 Admin (Whole Access)\n`admin`", use_container_width=True):
                    _do_demo_login("admin")
            with c_doc:
                if st.button("👨‍⚕️ Doctor (Dr. Sharma)\n`dr.sharma`", use_container_width=True):
                    _do_demo_login("dr.sharma")
                    
            c_nur, c_pat = st.columns(2)
            with c_nur:
                if st.button("👩‍⚕️ Nurse (Nurse Rao)\n`nurse.rao`", use_container_width=True):
                    _do_demo_login("nurse.rao")
            with c_pat:
                if st.button("🧑 Patient (Aarav Mehta)\n`aarav.mehta`", use_container_width=True):
                    _do_demo_login("aarav.mehta")

        st.markdown("</div>", unsafe_allow_html=True)


def _do_demo_login(username: str):
    st.session_state["username"] = username
    st.session_state["password"] = "password123"
    res = api_request("GET", "/auth/me")
    if res is not None and res.status_code == 200:
        st.session_state["user_info"] = res.json()
        st.rerun()
    else:
        st.error(f"Failed to authenticate demo user: {username}")


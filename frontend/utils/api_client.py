import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def get_auth():
    if "username" in st.session_state and "password" in st.session_state:
        return (st.session_state["username"], st.session_state["password"])
    return None


def api_request(method, endpoint, json=None, files=None, params=None, stop_on_unauth=False):
    url = f"{BASE_URL}{endpoint}"
    auth = get_auth()
    
    try:
        response = requests.request(
            method, url, json=json, auth=auth, files=files, params=params
        )
        
        if response.status_code == 401 and stop_on_unauth:
            st.session_state.clear()
            st.error(":material/lock: Session expired. Please log in again.")
            st.stop()
            
        return response
    except requests.exceptions.ConnectionError:
        st.error(f":material/cloud_off: Cannot connect to backend at {BASE_URL}. Ensure FastAPI is running.")
        return None
    except Exception as e:
        st.error(f"Request error: {e}")
        return None


def extract_error_detail(res, default="An unexpected error occurred."):
    """Extract a user-readable error detail string from response."""
    if res is None:
        return "Backend server is unreachable. Please verify that FastAPI is running."
    try:
        data = res.json()
        if isinstance(data, dict):
            detail = data.get("detail")
            if detail:
                if isinstance(detail, list):
                    errs = [f"{e.get('loc', [''])[-1]}: {e.get('msg')}" for e in detail if isinstance(e, dict)]
                    return "; ".join(errs)
                return str(detail)
            msg = data.get("message")
            if msg:
                return str(msg)
        return res.text[:250] or default
    except Exception:
        return res.text[:250] if hasattr(res, "text") and res.text else default


def handle_action_response(res, success_msg: str, error_prefix: str = "Action failed", rerun: bool = True) -> bool:
    """Evaluate API mutation response, dispatch persistent toast/banner, and optionally rerun."""
    from utils.ui_helpers import flash_success, flash_error
    if res is not None and 200 <= res.status_code < 300:
        flash_success(success_msg)
        if rerun:
            st.rerun()
        return True
    else:
        detail = extract_error_detail(res)
        code_str = f" [HTTP {res.status_code}]" if res is not None else ""
        flash_error(f"{error_prefix}{code_str}: {detail}")
        return False


# Convenient data loaders with safe fallbacks
def fetch_json(endpoint, default=None):
    if default is None:
        default = []
    res = api_request("GET", endpoint)
    if res is not None and res.status_code == 200:
        try:
            return res.json()
        except Exception:
            return default
    return default

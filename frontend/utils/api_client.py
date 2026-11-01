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
            st.error("🔒 Session expired. Please log in again.")
            st.stop()
            
        return response
    except requests.exceptions.ConnectionError:
        st.error(f"🔌 Cannot connect to backend at {BASE_URL}. Ensure FastAPI is running.")
        return None
    except Exception as e:
        st.error(f"Request error: {e}")
        return None


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

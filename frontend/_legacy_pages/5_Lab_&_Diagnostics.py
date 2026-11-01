import streamlit as st
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, page_header, check_login

st.set_page_config(page_title="Diagnostics", page_icon="🔬")
apply_theme()
check_login()
page_header("Lab & Diagnostics", "🔬", "Order tests and view results.")

tab1, tab2 = st.tabs(["View Orders", "Create Order"])

with tab1:
    v_id = st.number_input("Enter Visit ID to view orders", min_value=1, step=1)
    if st.button("Fetch Orders"):
        res = api_request("GET", f"/diagnostics/orders/visit/{v_id}")
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.info("No orders found for this visit.")

with tab2:
    with st.form("order_test"):
        visit_id = st.number_input("Visit ID", min_value=1, step=1)
        doctor_id = st.number_input("Doctor ID (Ordered By)", min_value=1, step=1)
        test_ids = st.text_input("Test IDs (comma separated, e.g., 1,2,3)")
        
        if st.form_submit_button("Order Tests"):
            ids = [int(i.strip()) for i in test_ids.split(",") if i.strip().isdigit()]
            payload = {"visit_id": visit_id, "ordered_by": doctor_id, "test_ids": ids, "status": "Ordered"}
            res = api_request("POST", "/diagnostics/orders", json=payload)
            if res.status_code == 201:
                st.success(f"✅ Tests ordered! Order ID: {res.json()['order_id']}")
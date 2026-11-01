import streamlit as st
from utils.api_client import api_request
from utils.ui_helpers import apply_theme, page_header, check_login
from utils.ai_engine import generate_mock_summary

st.set_page_config(page_title="AI Assistant", page_icon="🧠")
apply_theme()
check_login()
page_header("AI Clinical Assistant", "🧠", "Analyze clinical notes and generate summaries.")

st.info("Paste clinical notes below. The AI engine will extract symptoms and generate a summary.")

clinical_text = st.text_area("Clinical Notes", height=200, placeholder="Patient presents with severe cough, fever of 102F...")

if st.button("Analyze with AI", type="primary"):
    if clinical_text:
        with st.spinner("Analyzing text..."):
            summary = generate_mock_summary(clinical_text)
            st.markdown(summary)
    else:
        st.warning("Please enter some text to analyze.")
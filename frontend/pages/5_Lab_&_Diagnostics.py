"""
Lab & Diagnostics Management
Manages Diagnostic Catalog, Test Orders, Parameter Entry, Result Verification,
and Visual Biomarker Trend Analytics with AI Interpretation.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge
from utils.ai_engine import ai_engine

st.set_page_config(page_title="Labs & Diagnostics • HealthPulse", page_icon="🧪", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="Laboratory & Diagnostic Investigations",
    subtitle="Test Catalog, Order Requisitions, Parameter Analysis, Doctor Verification & AI Report Explainer",
    badge_text="Module 5",
    icon="🧪"
)

tabs = st.tabs(["🔬 Test Catalog", "📋 Order Lab Tests", "✍️ Enter & Verify Results", "📈 Patient Lab Trends & AI Explainer"])

# ------------------------------------------------------------------------------
# TAB 1: TEST CATALOG
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 🔬 Standard Diagnostic Catalog & Reference Ranges")
    
    tests = client.list_diagnostic_tests()
    col_t_list, col_t_add = st.columns([1.6, 1.2])

    with col_t_list:
        for t in tests:
            with st.expander(f"🧪 {t['test_name']} ({t.get('category')})", expanded=False):
                st.markdown(f"**Description:** {t.get('description', 'Standard diagnostic test')}")
                params = client.list_test_parameters(t["test_id"])
                if params:
                    p_df = pd.DataFrame(params)[["parameter_name", "unit", "reference_range"]]
                    st.dataframe(p_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("No individual parameters configured for this imaging / qualitative test.")

    with col_t_add:
        with st.expander("➕ Add New Diagnostic Test Panel", expanded=True):
            with st.form("new_test_form"):
                t_name = st.text_input("Test Name", placeholder="e.g. Renal Function Test (KFT), Liver Function Test (LFT)")
                t_cat = st.selectbox("Category", ["Blood", "Urine", "Imaging", "Other"])
                t_desc = st.text_area("Clinical Description", placeholder="e.g. Evaluates serum creatinine, BUN, electrolytes...")

                if st.form_submit_button("Add to Catalog", type="primary", use_container_width=True):
                    if t_name:
                        res = client.create_diagnostic_test({
                            "test_name": t_name,
                            "category": t_cat,
                            "description": t_desc
                        })
                        st.success(f"Test '{t_name}' created! Test ID: #{res['test_id']}")
                        st.rerun()

        with st.expander("➕ Add Parameter to Existing Test"):
            with st.form("new_param_form"):
                test_opts = {t["test_id"]: t["test_name"] for t in tests}
                target_t = st.selectbox("Target Test", options=list(test_opts.keys()), format_func=lambda x: test_opts.get(x))
                param_name = st.text_input("Parameter Name", placeholder="e.g. Serum Creatinine, Bilirubin Total")
                unit = st.text_input("Unit of Measure", placeholder="e.g. mg/dL, g/dL, %")
                ref_range = st.text_input("Standard Reference Range", placeholder="e.g. 0.7 - 1.3, < 200")

                if st.form_submit_button("Add Parameter", use_container_width=True):
                    if param_name:
                        new_p_id = max([p["parameter_id"] for p in client.mock_db["test_parameters"]], default=0) + 1
                        client.mock_db["test_parameters"].append({
                            "parameter_id": new_p_id,
                            "test_id": target_t,
                            "parameter_name": param_name,
                            "unit": unit,
                            "reference_range": ref_range
                        })
                        st.success(f"Parameter '{param_name}' linked to {test_opts[target_t]}!")
                        st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: ORDER LAB TESTS
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 📋 Clinical Test Requisition Order")
    
    col_ord_form, col_ord_list = st.columns([1.3, 1.5])

    with col_ord_form:
        with st.form("new_order_form"):
            patients = client.list_patients()
            pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']})" for p in patients}
            o_patient = st.selectbox("Patient", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

            doctors = client.list_doctors()
            doc_opts = {d["doctor_id"]: f"{d['full_name']} ({d['specialization']})" for d in docs}
            o_doctor = st.selectbox("Ordering Physician", options=list(doc_opts.keys()), format_func=lambda x: doc_opts.get(x))

            tests = client.list_diagnostic_tests()
            test_opts = {t["test_id"]: f"{t['test_name']} [{t['category']}]" for t in tests}
            selected_tests = st.multiselect("Select Diagnostic Tests to Order", options=list(test_opts.keys()), format_func=lambda x: test_opts.get(x))

            clinical_note = st.text_area("Clinical Indication / Physician Note", placeholder="e.g. Rule out anemia, routine pre-diabetic monitoring...")

            if st.form_submit_button("Submit Laboratory Order", type="primary", use_container_width=True):
                if selected_tests:
                    res = client.create_test_order({
                        "visit_id": 1,
                        "patient_id": o_patient,
                        "ordered_by": o_doctor,
                        "status": "Ordered",
                        "clinical_note": clinical_note,
                        "test_ids": selected_tests
                    })
                    st.success(f"Lab Order #{res['order_id']} dispatched successfully!")
                    st.rerun()
                else:
                    st.error("Please select at least one test to order.")

    with col_ord_list:
        st.markdown("#### Active & Completed Test Orders")
        orders = client.mock_db["test_orders"]
        for o in orders:
            p_obj = client.get_patient(o.get("patient_id", 4))
            doc_obj = client.get_doctor(o.get("ordered_by", 6))
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #0284c7;">Order #{o.get('order_id')}</span>
                    {render_status_badge(o.get('status', 'Ordered'))}
                </div>
                <div style="font-size: 0.85rem; color: #334155; margin-top: 0.35rem;">
                    <strong>Patient:</strong> {p_obj.get('full_name') if p_obj else f"Patient #{o.get('patient_id')}"} | <strong>Doctor:</strong> {doc_obj.get('full_name') if doc_obj else f"Doctor #{o.get('ordered_by')}"}
                </div>
                <div style="font-size: 0.825rem; color: #64748b; margin-top: 0.2rem;">
                    <strong>Indication:</strong> {o.get('clinical_note', 'N/A')}
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">
                    Date: {o.get('order_date','')[:16]}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: ENTER & VERIFY RESULTS
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### ✍️ Record & Physician Verification of Results")
    
    col_res_in, col_res_ver = st.columns([1.4, 1.4])

    with col_res_in:
        st.markdown("#### 🧪 Enter Results for Diagnostic Panel")
        with st.form("enter_result_form"):
            patients = client.list_patients()
            pat_opts = {p["patient_id"]: p["full_name"] for p in patients}
            res_patient = st.selectbox("Select Patient", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

            tests = client.list_diagnostic_tests()
            test_opts = {t["test_id"]: t["test_name"] for t in tests}
            res_test = st.selectbox("Diagnostic Test", options=list(test_opts.keys()), format_func=lambda x: test_opts.get(x))

            param_list = client.list_test_parameters(res_test)
            param_values = []
            
            if param_list:
                st.markdown("##### Parameter Values")
                for p in param_list:
                    c_p1, c_p2 = st.columns([2, 1])
                    with c_p1:
                        val = st.text_input(f"{p['parameter_name']} ({p.get('unit','')}) [Ref: {p.get('reference_range')}]", key=f"val_{p['parameter_id']}")
                    with c_p2:
                        flag = st.selectbox("Flag", ["Normal", "High", "Low"], key=f"flg_{p['parameter_id']}")
                    if val.strip():
                        param_values.append({
                            "parameter_id": p["parameter_id"],
                            "parameter_name": p["parameter_name"],
                            "result_value": val,
                            "flag": flag,
                            "unit": p.get("unit"),
                            "reference_range": p.get("reference_range")
                        })
            else:
                findings = st.text_area("Radiology / Qualitative Findings", placeholder="e.g. Normal cardiothoracic ratio, clear lung fields, no focal consolidation.")

            overall = st.text_area("Overall Pathologist / Radiologist Impression", placeholder="e.g. Findings compatible with mild allergic eosinophilia...")

            if st.form_submit_button("Save & Submit Lab Report", type="primary", use_container_width=True):
                new_res = client.create_test_result({
                    "order_item_id": 1,
                    "patient_id": res_patient,
                    "test_name": test_opts[res_test],
                    "report_date": datetime.now().isoformat(),
                    "overall_finding": overall,
                    "verified_by": None,
                    "verification_status": "Pending",
                    "items": param_values
                })
                st.success(f"Lab result for {test_opts[res_test]} recorded! Result ID: #{new_res['result_id']}")
                st.rerun()

    with col_res_ver:
        st.markdown("#### 🔍 Doctor Review & Verification Workflow")
        results = client.list_test_results()
        
        for r in results:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.15rem; margin-bottom: 0.85rem; border-left: 4px solid {'#10b981' if r.get('verification_status') == 'Verified' else '#f59e0b'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{r.get('test_name', 'Diagnostic Report')}</span>
                    {render_status_badge(r.get('verification_status', 'Pending'))}
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-top: 0.35rem;">
                    <strong>Report Date:</strong> {r.get('report_date','')[:16]} | <strong>Patient ID:</strong> #{r.get('patient_id')}
                </div>
                <div style="font-size: 0.825rem; color: #334155; margin-top: 0.25rem;">
                    <strong>Impression:</strong> {r.get('overall_finding')}
                </div>
                <div style="margin-top: 0.5rem; background: #f8fafc; padding: 0.5rem; border-radius: 6px;">
            """, unsafe_allow_html=True)

            for it in r.get("items", []):
                flag_color = "#dc2626" if it.get("flag") == "High" else ("#16a34a" if it.get("flag") == "Normal" else "#d97706")
                st.markdown(f"- **{it.get('parameter_name')}:** `{it.get('result_value')} {it.get('unit','')}` (<span style='color: {flag_color}; font-weight: 700;'>{it.get('flag')}</span>) [Ref: {it.get('reference_range')}]", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if r.get("verification_status") != "Verified":
                active_doc = st.session_state.get("active_doctor_id", 1)
                if st.button(f"Sign & Verify Report #{r['result_id']}", key=f"v_btn_{r['result_id']}", type="primary"):
                    client.verify_test_result(r["result_id"], verified_by=active_doc)
                    st.success(f"Report #{r['result_id']} officially signed and verified!")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 4: PATIENT LAB TRENDS & AI EXPLAINER
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 📈 Biomarker Longitudinal Trends & AI Report Explainer")
    
    patients = client.list_patients()
    pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']})" for p in patients}
    trend_patient_id = st.selectbox("Select Patient to View Biomarkers", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x), key="trend_pat")

    col_chart, col_ai_exp = st.columns([1.4, 1.4])

    with col_chart:
        st.markdown("#### 📊 Glycemic & Lipid Trends Over Time")
        
        # Sample realistic biomarker dataset for selected patient
        trend_data = pd.DataFrame({
            "Visit Date": ["2025-11-15", "2026-02-20", "2026-06-10", "2026-10-29"],
            "HbA1c (%)": [7.4, 6.9, 6.4, 6.1],
            "Fasting Glucose (mg/dL)": [165, 142, 128, 114],
            "Total Cholesterol (mg/dL)": [220, 205, 195, 185]
        }).set_index("Visit Date")

        st.line_chart(trend_data[["HbA1c (%)", "Fasting Glucose (mg/dL)"]])
        st.line_chart(trend_data[["Total Cholesterol (mg/dL)"]])

    with col_ai_exp:
        st.markdown("""
        <div class="glass-card" style="border: 1.5px solid #e9d5ff;">
            <div class="glass-card-header" style="color: #9333ea;">
                <span>✨ AI Lab Report Explainer</span>
                <span class="ai-badge">Dual Clinical & Patient View</span>
            </div>
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">
                Select or type any lab result to generate both doctor-level clinical interpretation and patient-friendly layperson explanations.
            </div>
        """, unsafe_allow_html=True)

        exp_param = st.selectbox("Biomarker", ["HbA1c (Glycated Hemoglobin)", "Total Cholesterol", "Hemoglobin", "Serum Creatinine", "WBC Count"])
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            val_input = st.text_input("Measured Value", value="6.1")
        with c_v2:
            flag_input = st.selectbox("Result Flag", ["High", "Normal", "Low"])

        if st.button("Generate AI Explanations", type="primary", use_container_width=True):
            exp = ai_engine.explain_lab_result(
                test_name="Diagnostic Test",
                param_name=exp_param,
                value=val_input,
                flag=flag_input,
                unit="%" if "HbA1c" in exp_param else "mg/dL",
                ref_range="4.0 - 5.6" if "HbA1c" in exp_param else "< 200"
            )
            
            st.markdown("##### 🩺 Clinical Assessment (For Doctor)")
            st.info(exp["doctor_insight"])

            st.markdown("##### 💬 Plain-English Explanation (For Patient)")
            st.success(exp["patient_translation"])

        st.markdown("</div>", unsafe_allow_html=True)

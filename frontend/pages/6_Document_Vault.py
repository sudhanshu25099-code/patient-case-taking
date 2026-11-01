"""
Medical Document Vault
Secure Medical Document Repository, File Uploads, Category & Tag Governance,
OCR Text Processing, and Document Verification.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime

from utils.api_client import client
from utils.ui_helpers import inject_custom_css, render_header, render_sidebar_context, render_status_badge

st.set_page_config(page_title="Document Vault • HealthPulse", page_icon="📁", layout="wide")
inject_custom_css()
render_sidebar_context(client)

render_header(
    title="Secure Medical Document Vault",
    subtitle="Encrypted Health Document Repository, Multi-Tag Taxonomy, OCR Text Extraction & Verification",
    badge_text="Module 6",
    icon="📁"
)

tabs = st.tabs(["📁 Document Library", "⬆️ Upload Medical File", "🔍 OCR Text & Verification"])

# ------------------------------------------------------------------------------
# TAB 1: DOCUMENT LIBRARY
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 📁 Patient Health Documents & Scans")
    
    patients = client.list_patients()
    pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']})" for p in patients}
    selected_pid = st.selectbox("Select Patient to Browse Vault", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

    docs = client.list_patient_documents(selected_pid)
    doc_types = client.list_document_types()
    type_map = {dt["document_type_id"]: dt["name"] for dt in doc_types}
    
    doc_tags = client.list_document_tags()
    tag_map = {t["tag_id"]: t["name"] for t in doc_tags}

    if docs:
        st.markdown(f"**Showing {len(docs)} Documents for {pat_opts[selected_pid]}**")
        for d in docs:
            t_name = type_map.get(d.get("document_type_id", 1), "Medical File")
            tag_badges = "".join([f"<span class='badge' style='background:#f1f5f9; color:#475569; margin-right:4px;'>#{tag_map.get(tid, 'Tag')}</span>" for tid in d.get("tag_ids", [])])
            
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.25rem; margin-bottom: 0.85rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.15rem; font-weight: 700; color: #0284c7;">📄 {d.get('title')}</span>
                        <span style="margin-left: 0.5rem;">{render_status_badge(d.get('verification_status', 'Verified'))}</span>
                    </div>
                    <span class="badge badge-active">{t_name}</span>
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-top: 0.4rem;">
                    {d.get('description', 'Uploaded clinical record.')}
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.35rem;">
                    <strong>Document Date:</strong> {d.get('document_date')} | <strong>File:</strong> <code>{d.get('file_path')}</code> ({round(d.get('file_size', 100000) / 1024)} KB)
                </div>
                <div style="margin-top: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>{tag_badges}</div>
                    <span style="font-size: 0.75rem; color: #94a3b8;">OCR Status: <strong>{d.get('ocr_status', 'Done')}</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"View Document Details & Extracted OCR for '{d.get('title')}'"):
                st.markdown(f"**OCR Extracted Content:**")
                st.markdown(f"<div class='soap-box'>{d.get('ocr_text', 'No text extracted.')}</div>", unsafe_allow_html=True)
                
                c_del1, c_del2 = st.columns([1, 4])
                with c_del1:
                    if st.button("Delete Document", key=f"del_{d['document_id']}", type="secondary"):
                        client.delete_document(d["document_id"])
                        st.warning("Document deleted from vault.")
                        st.rerun()
    else:
        st.info(f"No documents uploaded for {pat_opts[selected_pid]} yet. Use the Upload tab to add records.")

# ------------------------------------------------------------------------------
# TAB 2: UPLOAD MEDICAL DOCUMENT
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### ⬆️ Upload Clinical Document to Vault")
    
    with st.form("upload_doc_form"):
        patients = client.list_patients()
        pat_opts = {p["patient_id"]: f"{p['full_name']} (ID: #{p['patient_id']})" for p in patients}
        up_patient = st.selectbox("Target Patient", options=list(pat_opts.keys()), format_func=lambda x: pat_opts.get(x))

        doc_types = client.list_document_types()
        type_opts = {dt["document_type_id"]: dt["name"] for dt in doc_types}
        up_type = st.selectbox("Document Category", options=list(type_opts.keys()), format_func=lambda x: type_opts.get(x))

        uploaded_file = st.file_uploader("Select PDF or Image File", type=["pdf", "png", "jpg", "jpeg"])
        
        doc_title = st.text_input("Document Title", placeholder="e.g. Echo Cardiogram Doppler Report, Discharge Summary, Inhaler Prescription")
        doc_desc = st.text_area("Summary / Description", placeholder="e.g. Official diagnostic report performed by Apex Radiology Unit...")
        doc_date = st.date_input("Date of Document", value=date.today())

        doc_tags = client.list_document_tags()
        tag_opts = {t["tag_id"]: f"#{t['name']}" for t in doc_tags}
        selected_tags = st.multiselect("Assign Clinical Tags", options=list(tag_opts.keys()), format_func=lambda x: tag_opts.get(x))

        # Simulated OCR Option
        simulate_ocr = st.checkbox("Automatically extract text via Optical Character Recognition (OCR)", value=True)

        if st.form_submit_button("Upload & Index Document", type="primary", use_container_width=True):
            if doc_title.strip():
                fname = uploaded_file.name if uploaded_file else "document_upload.pdf"
                fsize = uploaded_file.size if uploaded_file else 250000
                m_type = uploaded_file.type if uploaded_file else "application/pdf"

                ocr_result = f"HEALTHCARE VAULT OCR INDEX • Title: {doc_title} • Extracted text content for patient #{up_patient}. Clinical summary validated." if simulate_ocr else "OCR not requested."

                client.upload_document({
                    "patient_id": up_patient,
                    "visit_id": 1,
                    "document_type_id": up_type,
                    "title": doc_title,
                    "description": doc_desc,
                    "file_path": f"/vault/docs/{fname}",
                    "file_size": fsize,
                    "mime_type": m_type,
                    "document_date": str(doc_date),
                    "ocr_text": ocr_result,
                    "ocr_status": "Done" if simulate_ocr else "Not Needed",
                    "verification_status": "Verified",
                    "uploaded_by": st.session_state.get("active_doctor_id", 1)
                }, tag_ids=selected_tags)

                st.success(f"Document '{doc_title}' successfully uploaded and encrypted in vault!")
                st.rerun()
            else:
                st.error("Please enter a document title.")

# ------------------------------------------------------------------------------
# TAB 3: OCR STATUS & VERIFICATION
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🔍 OCR Text Processing & Verification Queue")
    
    all_docs = client.mock_db["documents"]
    for d in all_docs:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1rem; margin-bottom: 0.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; color: #0f172a;">{d.get('title')}</span>
                <div>
                    <span style="margin-right: 0.5rem;">{render_status_badge(d.get('verification_status'))}</span>
                    <span class="badge badge-scheduled">OCR: {d.get('ocr_status')}</span>
                </div>
            </div>
            <div style="font-size: 0.825rem; color: #475569; margin-top: 0.25rem;">
                <strong>Path:</strong> <code>{d.get('file_path')}</code> | <strong>Patient ID:</strong> #{d.get('patient_id')}
            </div>
            <div class="soap-box" style="margin-top: 0.5rem; font-size: 0.8rem;">{d.get('ocr_text', 'No OCR text available')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if d.get("verification_status") != "Verified":
            if st.button(f"Verify Document #{d['document_id']}", key=f"ver_doc_{d['document_id']}", type="primary"):
                client.verify_document(d["document_id"])
                st.success("Document marked as Verified!")
                st.rerun()

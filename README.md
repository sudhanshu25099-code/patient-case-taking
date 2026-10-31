# Patient Case Taking & Record System 🏥

A comprehensive, secure healthcare management system designed to streamline patient records, clinical visits, diagnostics, and document management. 

This project features a **FastAPI** backend utilizing **raw SQL** (via SQLAlchemy) for high-performance database interactions, paired with a **Streamlit** dashboard for an intuitive, data-driven user interface.

## 🚀 Tech Stack

*   **Backend:** Python, FastAPI, SQLAlchemy (Engine/Connection only)
*   **Database:** MySQL (Raw SQL schema & queries)
*   **Frontend:** Streamlit
*   **Authentication:** HTTP Basic Auth (Password Hashing via `passlib[bcrypt]`)
*   **Data Validation:** Pydantic v2

## ✨ Core Features

1.  **Identity & Roles:** Manage Persons, Patients, Doctors, and Nurses with role-based access (Admin, Doctor, Nurse, Patient).
2.  **Hospital Management:** Manage hospitals, departments, and doctor-hospital affiliations.
3.  **Appointments:** Book, reschedule, and track appointment statuses (Scheduled, Completed, Cancelled).
4.  **Clinical Dashboard:** Record visits, diagnoses, procedures, prescriptions, and patient allergies/conditions.
5.  **Diagnostics:** Order lab tests, record results, and verify reports.
6.  **Document Vault:** Upload and tag medical documents (PDF/Images) with OCR status tracking.
7.  **Consent Management:** Grant or revoke doctor access to specific patient records.
8.  **Pre-Visit Summaries:** Utilizes an optimized SQL View (`v_previsit_snapshot`) to generate a comprehensive 360-degree view of a patient's health before a doctor's appointment.

---

## 🛠️ Project Structure

```text
patient-case-taking/
│
├── backend/                  # FastAPI Application
│   ├── config.py             # Environment variables
│   ├── database.py           # SQLAlchemy engine
│   ├── dependencies.py       # FastAPI dependency injection
│   ├── main.py               # App entry point & router registration
│   ├── requirements.txt
│   ├── queries/              # Raw SQL queries
│   ├── routes/               # API Endpoints
│   └── schemas/              # Pydantic models
│
├── frontend/                 # Streamlit Dashboard
│   ├── app.py                # Login & Home page
│   ├── pages/                # Multipage dashboard (Appointments, Labs, etc.)
│   ├── utils/                # API Client (communicates with backend)
│   └── requirements.txt
│
└── db_schema/                # Database SQL Scripts
    ├── 01_user_hospital_schema.sql
    ├── 02_clinical_schema.sql
    ├── 03_document_consent_schema.sql
    ├── 04_logging_schema.sql
    └── 05_seed.sql

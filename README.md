# Clinical EHR — Connected Care Workspace 🏥

A full-stack, enterprise-grade Electronic Health Record (EHR) and Clinical Case-Taking platform designed to streamline multi-hospital healthcare delivery. The system unites hospital administration, outpatient consultation workflows, nursing triage, diagnostics, document management, patient self-service, and LLM-powered clinical summarization into a single connected ecosystem.

---

## 🏛️ System Architecture

Built on a three-tier, decoupled architecture:

* **Presentation Layer (Frontend):** Modern multi-page **Streamlit** application utilizing role-isolated navigation (`st.navigation`), responsive wide-angle KPI cards, toast notifications, and dynamic perspective switching.
* **Service Layer (Backend):** High-performance **FastAPI** REST engine with Pydantic v2 validation, modular route controllers, and raw parameterized SQL execution (via SQLAlchemy connection pooling).
* **Intelligence Layer (AI Engine):** **Groq LLM API** (`openai/gpt-oss-20b` / `qwen/qwen3.8-27b`) for real-time clinical notes extraction, visit episode summarization, and longitudinal patient handover generation.
* **Data Layer (Database):** **MySQL 8.x** relational store normalized across 38 domain tables plus an optimized SQL aggregation view (`v_previsit_snapshot`).

---

## 👥 Role-Based Portals & Key Features

### 1. 🛡️ Super Admin & Hospital Admin Portal
* **Executive Command Center:** 6 wide-angle KPI flashcards in a compact 2-row × 3-column layout (Patients, Doctors, Nurses, Hospitals, Appointments, Lab Catalog) with rich demographic and operational detail pills.
* **Facility & Department Administration:** Register network hospitals, clinical departments (e.g. Cardiology, OPD), and manage doctor affiliations.
* **User & Identity Hub:** Manage unified `person` entities, patient profiles, medical doctor credentials, nurse shifts, system accounts, and assign granular security roles.
* **Master Appointments Ledger:** Real-time visibility and status management across all enterprise bookings.
* **Clinical Vault & Oversight:** Read-only inspection of clinical encounters, ICD-10 diagnoses, prescriptions, and lab orders.
* **Security & Audit Logs:** Raw table-level change logs (with old/new JSON states), system notifications, and a live MySQL `PROCESSLIST` thread monitor.
* **Groq AI Administration:** Runtime configuration of Groq API keys and default model switching without server restarts.
* **Admin Perspective Switcher:** Enables administrators to preview and simulate Doctor, Nurse, or Patient portal views on demand.

### 2. 🩺 Doctor Portal
* **Doctor Station & Queue:** Real-time OPD appointment queue with status indicators (Pending/Completed) and quick consultation kickoff.
* **Clinical Case Taking (Consultation Engine):**
  * **Pre-Visit Snapshot:** Auto-loads patient history, today's reported symptoms, and active allergy alerts from `v_previsit_snapshot`.
  * **Clinical Visit & Procedures:** Record encounters (OPD/IPD/ER), chief complaints, vitals, and attach performed clinical procedures with outcome notes.
  * **ICD-10 Diagnoses:** Record primary, secondary, and provisional diagnoses with diagnostic rationale.
  * **Prescriptions:** Issue medication orders with structured dosages, frequencies, duration, routes, and instructions.
  * **SOAP Notes:** Clinical documentation formatted in Subjective, Objective, Assessment, and Plan sections.
  * **Episode Medical Summary:** Conclude consultation by packaging visit data into permanent `medical_summary` records and sealing the appointment.
* **Lab & Diagnostics:** Multiselect test ordering from the diagnostic catalog and physician verification of pathology/imaging results.
* **Patient EMR Vault:** Search patient histories, verify active consent authorizations, and inspect past conditions/documents.
* **AI Clinical Assistant:** On-demand summarization of raw clinical text, database-backed visit episode generation, and patient longitudinal summaries.

### 3. 🩹 Nurse Portal
* **Clinic Triage Queue:** Real-time intake queue with status tracking for scheduled patients.
* **Check-In & Vitals Intake:** Record intake vitals (BP, HR, SpO2, Temperature, Weight), today's reported symptoms, and pre-visit notes.
* **Allergies & Care Records:** Record and resolve patient allergies (Drug, Food, Environmental) and chronic/past illnesses.
* **Lab Orders Tracking:** Update diagnostic order statuses (`Ordered` → `Processing` → `Completed`) and publish lab test findings.
* **Patient Directory:** Demographics lookup and direct medical document upload into patient vaults.

### 4. 👤 Patient Portal
* **My Health Profile:** Personal demographics, ABHA connection status, active medical conditions, and known allergies.
* **My Appointments:** Appointment history tracking and self-service booking across network hospitals and doctors.
* **My Medical Records:** Review past visit encounter notes and clinical episode summaries.
* **My Diagnostic Reports:** Access completed laboratory results and verified findings.
* **Document Vault:** Securely inspect, view metadata, and delete personal health records.
* **Consent & Privacy:** Granular data-sharing control—grant or revoke access permissions to specific doctors.

---

## 🤖 Groq AI Intelligence Engine

The platform integrates server-side Groq LLM processing via dedicated `/ai/*` endpoints:

| Endpoint | Method | Input Source | Output Description |
|---|---|---|---|
| `/ai/summarize` | `POST` | Raw free-text | Structured clinical report with extracted symptoms and recommendations |
| `/ai/summarize/visit` | `POST` | `visit_id` (DB) | Comprehensive episode/discharge summary aggregating vitals, diagnoses, Rx, and procedures |
| `/ai/summarize/patient` | `POST` | `patient_id` (DB) | Longitudinal handover report aggregating conditions, allergies, last 5 visits, and prior summaries |
| `/ai/config` | `GET` | — | Current key status (redacted) and active Groq model |
| `/ai/config/key` | `PUT` | `api_key` | Updates Groq key at runtime in `.env` and memory without server restart |

---

## 🗄️ Database Architecture & Implementation

The MySQL schema is partitioned into modular functional domains:

```
patient_record_system (MySQL 8.x)
├── Identity & Auth (7 tables)
│   ├── person                  # Base entity (full_name, DOB, gender, phone, email, address)
│   ├── user_account            # Credentials & authentication
│   ├── role                    # Role definitions (Super Admin, Hospital Admin, Doctor, Nurse, Patient)
│   ├── user_role               # Many-to-many user-to-role mappings
│   ├── patient_profile         # Patient metrics (blood_group, ABHA status, emergency contact)
│   ├── doctor_profile          # Medical licensing, specialization, experience, OPD fee
│   └── nurse_profile           # Nursing shifts, departments, employee IDs
│
├── Hospital & Facility (3 tables)
│   ├── hospital                # Multi-branch facility records
│   ├── department              # Clinical units per hospital (Cardiology, Pediatrics, etc.)
│   └── doctor_hospital         # Staff affiliations and joining dates
│
├── Appointments & Intake (3 tables + 1 view)
│   ├── appointment             # Master consultation schedule and lifecycle status
│   ├── appointment_symptom     # Nurse-recorded intake symptoms
│   ├── appointment_note        # Consultation and SOAP notes
│   └── v_previsit_snapshot     # SQL View aggregating patient profile, allergies, conditions & prior summary
│
├── Clinical Consultation & EMR (8 tables)
│   ├── visit                   # Clinical encounters (OPD/IPD/ER, chief complaint, vitals)
│   ├── visit_diagnosis         # ICD-10 coded diagnostic records
│   ├── visit_procedure         # Procedures performed during encounters
│   ├── visit_note              # Encounter-specific notes
│   ├── allergy                 # Patient allergy registers (reactions, severity, status)
│   ├── patient_condition       # Chronic and past medical illnesses
│   ├── prescription            # Prescription order headers
│   └── prescription_item       # Medication line items (dose, route, frequency, duration)
│
├── Diagnostics & Pathology (6 tables)
│   ├── diagnostic_test         # Laboratory catalog
│   ├── test_parameter          # Test analytes and normal ranges
│   ├── test_order              # Order tracking (Ordered / Processing / Completed)
│   ├── test_order_item         # Ordered catalog items
│   ├── test_result             # Findings and physician verification flags
│   └── test_result_item        # Measured analyte values
│
├── Document Vault & Consent (6 tables)
│   ├── medical_document        # Uploaded files metadata, MIME types, and verification status
│   ├── document_type           # Categorization categories
│   ├── document_tag            # Tag registry
│   ├── document_tag_mapping    # Multi-tag assignments
│   ├── patient_consent         # Patient-to-doctor data authorization grants
│   └── consent_access          # Audit trail of record access under active consents
│
└── Intelligence & Auditing (5 tables)
    ├── medical_summary         # Permanent episode summaries (pre-visit, discharge, AI-generated)
    ├── summary_document        # Summary-to-document relationships
    ├── notification            # User system notifications
    ├── access_log              # Granular user access logs
    └── audit_trail             # Database-level mutation audit (INSERT/UPDATE/DELETE with JSON deltas)
```

---

## 🔒 Role ↔ Feature Access Matrix

| Feature Area | Super Admin | Hospital Admin | Doctor | Nurse | Patient |
|---|:---:|:---:|:---:|:---:|:---:|
| **Executive KPI Dashboard** | ✓ Full | ✓ Full | — | — | — |
| **Hospital / Dept Administration** | ✓ Full | ✓ Full | — | — | — |
| **User & Role Management** | ✓ Full | View | — | — | — |
| **Appointment Booking & Status** | ✓ Full | ✓ Full | View Assigned | ✓ Triage | ✓ Self |
| **Clinical Consultation & Case Taking**| View | View | ✓ Full | — | — |
| **Prescriptions & Diagnoses (ICD-10)** | View | View | ✓ Full | — | View Self |
| **Intake Vitals & Symptoms** | View | View | View | ✓ Full | — |
| **Allergy & Condition Registers** | View | View | ✓ Full | ✓ Full | View Self |
| **Diagnostic Test Orders** | View | View | ✓ Order | ✓ Track | — |
| **Lab Results & Verification** | View | View | ✓ Verify | ✓ Record | View Self |
| **Medical Document Vault** | ✓ Full | ✓ Full | Verify | Upload | Self / Delete |
| **Episode Medical Summaries** | View | View | ✓ Create | — | View Self |
| **Patient Consent Control** | View | View | Check | — | ✓ Full |
| **Audit Trails & DB Processlist** | ✓ Full | View | — | — | — |
| **Groq AI Clinical Assistant** | ✓ Full | ✓ Full | ✓ Full | — | — |
| **Groq API Key / Model Settings** | ✓ Full | — | — | — | — |
| **Admin Perspective Switcher** | ✓ Full | ✓ Full | — | — | — |

---

## 📂 Project Organization

```text
patient-case-taking/
├── backend/
│   ├── config.py             # Pydantic BaseSettings, DB connection strings & Groq settings
│   ├── database.py           # SQLAlchemy database engine configuration
│   ├── dependencies.py       # FastAPI dependency injection (DB connection providers)
│   ├── main.py               # Application factory, middleware & router bindings
│   ├── queries/              # Modular raw SQL query definitions
│   ├── routes/               # API route controllers (identity, hospital, visits, ai, etc.)
│   └── schemas/              # Pydantic v2 request/response validation schemas
│
├── frontend/
│   ├── app.py                # App entrypoint, role-based navigation & theme layout
│   ├── assets/               # Brand logos and icons
│   ├── utils/
│   │   ├── ai_engine.py      # Groq AI backend client with fallback handling
│   │   ├── api_client.py     # Centralized HTTP request helper & flash messaging
│   │   └── ui_helpers.py     # CSS styling, wide-angle KPI cards & role badges
│   └── views/
│       ├── admin_views.py    # Executive overview, identity hub, hospital admin, audit
│       ├── auth_view.py      # Unified login screen & demo credentials
│       ├── doctor_views.py   # OPD queue, case taking, diagnostics, EMR vault, AI
│       ├── nurse_views.py    # Triage, check-in vitals, care records, lab tracking
│       └── patient_views.py  # Health profile, appointments, summaries, consent
│
└── database/                 # Database initialization, schemas, triggers, and seed scripts
    ├── 01_user_hospital_schema.sql
    ├── 02_clinical_schema.sql
    ├── 03_document_consent_schema.sql
    ├── 04_logging_schema.sql
    └── 05_seed.sql
```

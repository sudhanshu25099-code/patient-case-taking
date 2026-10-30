-- 03_document_consent_schema.sql
-- Medical Documents (6) + Consent & Access (7) + Medical Summary (8)
-- Run order: run after 02

USE patient_record_system;

-- =====================================================================
-- 6. MEDICAL DOCUMENTS
-- =====================================================================

CREATE TABLE document_type (
    document_type_id   SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(100) NOT NULL,           -- Prescription, Lab Report, X-Ray, Discharge Summary ...
    description        VARCHAR(255),
    UNIQUE KEY uq_doctype_name (name)
) ENGINE=InnoDB;

CREATE TABLE document_tag (
    tag_id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(80) NOT NULL,
    description        VARCHAR(255),
    UNIQUE KEY uq_tag_name (name)
) ENGINE=InnoDB;

CREATE TABLE medical_document (
    document_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id         INT UNSIGNED NOT NULL,
    visit_id           INT UNSIGNED NULL,
    document_type_id   SMALLINT UNSIGNED NOT NULL,
    test_result_id     INT UNSIGNED NULL,               -- NEW: link uploaded report to a result
    title              VARCHAR(200) NOT NULL,
    description        TEXT,
    file_path          VARCHAR(500) NOT NULL,
    file_size          BIGINT UNSIGNED,
    mime_type          VARCHAR(100),
    document_date      DATE,
    ocr_text           MEDIUMTEXT NULL,
    ocr_status         ENUM('Pending','Done','Failed','Not Needed') NOT NULL DEFAULT 'Pending',
    verification_status ENUM('Pending','Verified','Rejected') NOT NULL DEFAULT 'Pending',
    uploaded_by        INT UNSIGNED NOT NULL,
    uploaded_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_doc_patient (patient_id, document_date),
    FULLTEXT KEY ft_doc_ocr (title, ocr_text),
    CONSTRAINT fk_doc_patient FOREIGN KEY (patient_id)       REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_doc_visit   FOREIGN KEY (visit_id)         REFERENCES visit(visit_id),
    CONSTRAINT fk_doc_type    FOREIGN KEY (document_type_id) REFERENCES document_type(document_type_id),
    CONSTRAINT fk_doc_result  FOREIGN KEY (test_result_id)   REFERENCES test_result(result_id),
    CONSTRAINT fk_doc_user    FOREIGN KEY (uploaded_by)      REFERENCES user_account(user_id)
) ENGINE=InnoDB;

CREATE TABLE document_tag_mapping (                     -- Document M : N Tag
    document_id        INT UNSIGNED NOT NULL,
    tag_id             INT UNSIGNED NOT NULL,
    PRIMARY KEY (document_id, tag_id),
    CONSTRAINT fk_dtm_doc FOREIGN KEY (document_id) REFERENCES medical_document(document_id) ON DELETE CASCADE,
    CONSTRAINT fk_dtm_tag FOREIGN KEY (tag_id)      REFERENCES document_tag(tag_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================================
-- 7. CONSENT & ACCESS CONTROL
-- =====================================================================

CREATE TABLE patient_consent (
    consent_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id         INT UNSIGNED NOT NULL,
    hospital_id        INT UNSIGNED NULL,
    consent_type       ENUM('View Only') NOT NULL DEFAULT 'View Only',
    valid_from         DATETIME NOT NULL,
    valid_to           DATETIME NULL,
    status             ENUM('Active','Revoked','Expired') NOT NULL DEFAULT 'Active',
    purpose            VARCHAR(255),
    remarks            VARCHAR(255),
    KEY idx_consent_patient (patient_id, status),
    CONSTRAINT fk_consent_patient  FOREIGN KEY (patient_id)  REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_consent_hospital FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
) ENGINE=InnoDB;

CREATE TABLE consent_access (
    access_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    consent_id         INT UNSIGNED NOT NULL,
    doctor_id          INT UNSIGNED NULL,
    department_id      INT UNSIGNED NULL,
    access_from        DATETIME NOT NULL,
    access_to          DATETIME NULL,
    status             ENUM('Active','Revoked','Expired') NOT NULL DEFAULT 'Active',
    KEY idx_cacc_consent (consent_id),
    CONSTRAINT fk_cacc_consent FOREIGN KEY (consent_id)    REFERENCES patient_consent(consent_id) ON DELETE CASCADE,
    CONSTRAINT fk_cacc_doctor  FOREIGN KEY (doctor_id)     REFERENCES doctor_profile(doctor_id),
    CONSTRAINT fk_cacc_dept    FOREIGN KEY (department_id) REFERENCES department(department_id),
    -- at least one of doctor / department must be given
    CONSTRAINT chk_cacc_target CHECK (doctor_id IS NOT NULL OR department_id IS NOT NULL)
) ENGINE=InnoDB;

-- =====================================================================
-- 8. MEDICAL SUMMARY
-- =====================================================================

CREATE TABLE medical_summary (
    summary_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id         INT UNSIGNED NOT NULL,
    appointment_id     INT UNSIGNED NULL,               -- NEW: pre-visit summary for this appointment
    summary_type       ENUM('Pre-visit','Discharge','General') NOT NULL DEFAULT 'Pre-visit',
    summary_text       MEDIUMTEXT NOT NULL,
    generated_by       ENUM('Manual','AI','System') NOT NULL DEFAULT 'System',
    generated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version_no         INT UNSIGNED NOT NULL DEFAULT 1,
    is_current         BOOLEAN NOT NULL DEFAULT TRUE,
    KEY idx_sum_patient (patient_id, is_current),
    KEY idx_sum_appt (appointment_id),
    CONSTRAINT fk_sum_patient FOREIGN KEY (patient_id)     REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_sum_appt    FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id)
) ENGINE=InnoDB;

CREATE TABLE summary_document (                         -- Summary M : N Document (source records)
    summary_id         INT UNSIGNED NOT NULL,
    document_id        INT UNSIGNED NOT NULL,
    notes              VARCHAR(255),
    PRIMARY KEY (summary_id, document_id),
    CONSTRAINT fk_sd_summary FOREIGN KEY (summary_id)  REFERENCES medical_summary(summary_id) ON DELETE CASCADE,
    CONSTRAINT fk_sd_doc     FOREIGN KEY (document_id) REFERENCES medical_document(document_id)
) ENGINE=InnoDB;
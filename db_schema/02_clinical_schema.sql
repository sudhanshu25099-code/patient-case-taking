-- 02_clinical_schema.sql
-- Appointments (3) + Visits & Clinical (4) + Diagnostic Tests (5)
-- Run order: run after 01

USE patient_record_system;

-- =====================================================================
-- 3. APPOINTMENTS
-- =====================================================================

CREATE TABLE appointment (
    appointment_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id         INT UNSIGNED NOT NULL,
    hospital_id        INT UNSIGNED NOT NULL,
    doctor_id          INT UNSIGNED NOT NULL,
    appointment_date   DATE NOT NULL,
    time_slot          TIME NOT NULL,
    reason             VARCHAR(255),
    pre_visit_notes    TEXT NULL,                       -- NEW: patient's own notes before visit
    is_follow_up       BOOLEAN NOT NULL DEFAULT FALSE,  -- NEW
    status             ENUM('Scheduled','Completed','Cancelled','No Show') NOT NULL DEFAULT 'Scheduled',
    notes              TEXT,
    booked_by          INT UNSIGNED NULL,               -- NEW: user who booked
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,   -- NEW
    KEY idx_appt_patient (patient_id, appointment_date),
    KEY idx_appt_doctor_slot (doctor_id, appointment_date, time_slot),
    CONSTRAINT fk_appt_patient  FOREIGN KEY (patient_id)  REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_appt_hospital FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id),
    CONSTRAINT fk_appt_doctor   FOREIGN KEY (doctor_id)   REFERENCES doctor_profile(doctor_id),
    CONSTRAINT fk_appt_bookedby FOREIGN KEY (booked_by)   REFERENCES user_account(user_id)
) ENGINE=InnoDB;

-- NEW: structured "today's symptoms" entered at booking time
CREATE TABLE appointment_symptom (
    symptom_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id     INT UNSIGNED NOT NULL,
    symptom_name       VARCHAR(150) NOT NULL,
    severity           ENUM('Mild','Moderate','Severe') NULL,
    since_date         DATE NULL,
    notes              VARCHAR(255),
    KEY idx_asym_appt (appointment_id),
    CONSTRAINT fk_asym_appt FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE appointment_note (
    appt_note_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id     INT UNSIGNED NOT NULL,
    note_text          TEXT NOT NULL,
    added_by           INT UNSIGNED NOT NULL,
    added_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_anote_appt (appointment_id),
    CONSTRAINT fk_anote_appt FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id) ON DELETE CASCADE,
    CONSTRAINT fk_anote_user FOREIGN KEY (added_by)       REFERENCES user_account(user_id)
) ENGINE=InnoDB;

-- =====================================================================
-- 4. VISITS & CLINICAL INFORMATION
-- =====================================================================

CREATE TABLE visit (
    visit_id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id     INT UNSIGNED NULL,               -- NEW: Appointment 1 : 0..1 Visit
    patient_id         INT UNSIGNED NOT NULL,
    hospital_id        INT UNSIGNED NOT NULL,
    department_id      INT UNSIGNED NULL,
    doctor_id          INT UNSIGNED NULL,
    visit_date         DATETIME NOT NULL,
    visit_type         ENUM('OPD','IPD','ER','Other') NOT NULL DEFAULT 'OPD',
    chief_complaint    VARCHAR(255),
    symptoms           TEXT,
    vitals_summary     VARCHAR(500),
    notes              TEXT,
    UNIQUE KEY uq_visit_appt (appointment_id),
    KEY idx_visit_patient (patient_id, visit_date),
    CONSTRAINT fk_visit_appt     FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id),
    CONSTRAINT fk_visit_patient  FOREIGN KEY (patient_id)     REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_visit_hospital FOREIGN KEY (hospital_id)    REFERENCES hospital(hospital_id),
    CONSTRAINT fk_visit_dept     FOREIGN KEY (department_id)  REFERENCES department(department_id),
    CONSTRAINT fk_visit_doctor   FOREIGN KEY (doctor_id)      REFERENCES doctor_profile(doctor_id)
) ENGINE=InnoDB;

CREATE TABLE visit_diagnosis (
    diagnosis_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    visit_id           INT UNSIGNED NOT NULL,
    diagnosis_code     VARCHAR(20) NULL,                -- optional (ICD-10)
    diagnosis_name     VARCHAR(255) NOT NULL,
    diagnosis_type     ENUM('Primary','Secondary','Provisional') NOT NULL DEFAULT 'Primary',
    notes              TEXT,
    KEY idx_vdiag_visit (visit_id),
    CONSTRAINT fk_vdiag_visit FOREIGN KEY (visit_id) REFERENCES visit(visit_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE visit_procedure (
    procedure_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    visit_id           INT UNSIGNED NOT NULL,
    procedure_name     VARCHAR(255) NOT NULL,
    procedure_type     VARCHAR(100),
    notes              TEXT,
    KEY idx_vproc_visit (visit_id),
    CONSTRAINT fk_vproc_visit FOREIGN KEY (visit_id) REFERENCES visit(visit_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE visit_note (
    note_id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    visit_id           INT UNSIGNED NOT NULL,
    note_type          ENUM('Consultation','Follow-up','Other') NOT NULL DEFAULT 'Consultation',
    title              VARCHAR(200),
    content            TEXT NOT NULL,
    added_by           INT UNSIGNED NOT NULL,
    added_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_vnote_visit (visit_id),
    CONSTRAINT fk_vnote_visit FOREIGN KEY (visit_id) REFERENCES visit(visit_id) ON DELETE CASCADE,
    CONSTRAINT fk_vnote_user  FOREIGN KEY (added_by) REFERENCES user_account(user_id)
) ENGINE=InnoDB;

-- NEW: allergies (replaces the old PERSON.allergies text column)
CREATE TABLE allergy (
    allergy_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id         INT UNSIGNED NOT NULL,
    allergen           VARCHAR(150) NOT NULL,
    allergy_type       ENUM('Drug','Food','Environmental','Other') NOT NULL,
    reaction           VARCHAR(255),
    severity           ENUM('Mild','Moderate','Severe') NULL,
    status             ENUM('Active','Resolved') NOT NULL DEFAULT 'Active',
    noted_date         DATE,
    recorded_by        INT UNSIGNED NULL,
    notes              VARCHAR(255),
    KEY idx_allergy_patient (patient_id, status),
    CONSTRAINT fk_allergy_patient FOREIGN KEY (patient_id)  REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_allergy_user    FOREIGN KEY (recorded_by) REFERENCES user_account(user_id)
) ENGINE=InnoDB;

-- NEW: chronic conditions / past illness / surgery / family history
CREATE TABLE patient_condition (
    condition_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id         INT UNSIGNED NOT NULL,
    source_visit_id    INT UNSIGNED NULL,
    condition_name     VARCHAR(200) NOT NULL,
    icd_code           VARCHAR(20) NULL,
    condition_type     ENUM('Chronic','Past illness','Surgery','Family history') NOT NULL,
    onset_date         DATE NULL,
    status             ENUM('Active','Controlled','Resolved') NOT NULL DEFAULT 'Active',
    notes              TEXT,
    KEY idx_cond_patient (patient_id, status),
    CONSTRAINT fk_cond_patient FOREIGN KEY (patient_id)      REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_cond_visit   FOREIGN KEY (source_visit_id) REFERENCES visit(visit_id)
) ENGINE=InnoDB;

-- NEW: prescriptions & medicines
CREATE TABLE prescription (
    prescription_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    visit_id           INT UNSIGNED NOT NULL,
    patient_id         INT UNSIGNED NOT NULL,
    doctor_id          INT UNSIGNED NOT NULL,
    prescribed_date    DATE NOT NULL,
    notes              TEXT,
    KEY idx_presc_patient (patient_id, prescribed_date),
    CONSTRAINT fk_presc_visit   FOREIGN KEY (visit_id)   REFERENCES visit(visit_id),
    CONSTRAINT fk_presc_patient FOREIGN KEY (patient_id) REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_presc_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctor_profile(doctor_id)
) ENGINE=InnoDB;

CREATE TABLE prescription_item (
    item_id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    prescription_id    INT UNSIGNED NOT NULL,
    medicine_name      VARCHAR(200) NOT NULL,
    dosage             VARCHAR(80),
    frequency          VARCHAR(80),
    route              VARCHAR(40),
    duration_days      SMALLINT UNSIGNED,
    start_date         DATE,
    end_date           DATE,
    is_ongoing         BOOLEAN NOT NULL DEFAULT FALSE,
    instructions       VARCHAR(255),
    KEY idx_pitem_presc (prescription_id),
    CONSTRAINT fk_pitem_presc FOREIGN KEY (prescription_id) REFERENCES prescription(prescription_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================================
-- 5. DIAGNOSTIC TESTS & RESULTS
-- =====================================================================

CREATE TABLE diagnostic_test (
    test_id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    test_name          VARCHAR(200) NOT NULL,
    category           ENUM('Blood','Urine','Imaging','Other') NOT NULL,
    description        VARCHAR(255),
    UNIQUE KEY uq_test_name (test_name)
) ENGINE=InnoDB;

-- NEW: parameters of a test (e.g. CBC -> Hemoglobin, WBC ...)
CREATE TABLE test_parameter (
    parameter_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    test_id            INT UNSIGNED NOT NULL,
    parameter_name     VARCHAR(150) NOT NULL,
    unit               VARCHAR(30),
    reference_range    VARCHAR(80),
    UNIQUE KEY uq_param (test_id, parameter_name),
    CONSTRAINT fk_param_test FOREIGN KEY (test_id) REFERENCES diagnostic_test(test_id)
) ENGINE=InnoDB;

CREATE TABLE test_order (
    order_id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    visit_id           INT UNSIGNED NOT NULL,
    ordered_by         INT UNSIGNED NOT NULL,           -- doctor
    order_date         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status             ENUM('Ordered','Completed','Cancelled') NOT NULL DEFAULT 'Ordered',
    clinical_note      TEXT,
    KEY idx_torder_visit (visit_id),
    CONSTRAINT fk_torder_visit  FOREIGN KEY (visit_id)   REFERENCES visit(visit_id),
    CONSTRAINT fk_torder_doctor FOREIGN KEY (ordered_by) REFERENCES doctor_profile(doctor_id)
) ENGINE=InnoDB;

CREATE TABLE test_order_item (
    order_item_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id           INT UNSIGNED NOT NULL,
    test_id            INT UNSIGNED NOT NULL,
    status             ENUM('Pending','Completed') NOT NULL DEFAULT 'Pending',
    KEY idx_toi_order (order_id),
    CONSTRAINT fk_toi_order FOREIGN KEY (order_id) REFERENCES test_order(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_toi_test  FOREIGN KEY (test_id)  REFERENCES diagnostic_test(test_id)
) ENGINE=InnoDB;

CREATE TABLE test_result (
    result_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_item_id      INT UNSIGNED NOT NULL,
    report_date        DATETIME NOT NULL,
    overall_finding    TEXT,
    verified_by        INT UNSIGNED NULL,
    verification_status ENUM('Pending','Verified','Rejected') NOT NULL DEFAULT 'Pending',
    UNIQUE KEY uq_result_item (order_item_id),          -- OrderItem 1 : 1 Result
    CONSTRAINT fk_result_item FOREIGN KEY (order_item_id) REFERENCES test_order_item(order_item_id),
    CONSTRAINT fk_result_user FOREIGN KEY (verified_by)   REFERENCES user_account(user_id)
) ENGINE=InnoDB;

CREATE TABLE test_result_item (
    result_item_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    result_id          INT UNSIGNED NOT NULL,
    parameter_id       INT UNSIGNED NOT NULL,
    result_value       VARCHAR(100) NOT NULL,
    flag               ENUM('Normal','High','Low') NULL,
    notes              VARCHAR(255),
    KEY idx_tri_result (result_id),
    CONSTRAINT fk_tri_result FOREIGN KEY (result_id)    REFERENCES test_result(result_id) ON DELETE CASCADE,
    CONSTRAINT fk_tri_param  FOREIGN KEY (parameter_id) REFERENCES test_parameter(parameter_id)
) ENGINE=InnoDB;
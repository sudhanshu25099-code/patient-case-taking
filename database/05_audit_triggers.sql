-- ============================================================
-- Clinical EHR — Audit Trail MySQL Triggers
-- Auto-populates audit_trail table on INSERT / UPDATE / DELETE
-- across all critical clinical tables.
-- ============================================================

USE patient_record_system;

DELIMITER $$

-- ============================================================
-- TABLE: appointment
-- ============================================================
DROP TRIGGER IF EXISTS trg_appointment_insert $$
CREATE TRIGGER trg_appointment_insert
AFTER INSERT ON appointment FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.booked_by,
        'appointment',
        NEW.appointment_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'doctor_id', NEW.doctor_id,
            'appointment_date', NEW.appointment_date,
            'time_slot', NEW.time_slot,
            'status', NEW.status,
            'reason', NEW.reason
        ),
        'Appointment booked'
    );
END $$

DROP TRIGGER IF EXISTS trg_appointment_update $$
CREATE TRIGGER trg_appointment_update
AFTER UPDATE ON appointment FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status OR OLD.appointment_date != NEW.appointment_date OR OLD.doctor_id != NEW.doctor_id THEN
        INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
        VALUES (
            NEW.booked_by,
            'appointment',
            NEW.appointment_id,
            'UPDATE',
            JSON_OBJECT(
                'status', OLD.status,
                'appointment_date', OLD.appointment_date,
                'doctor_id', OLD.doctor_id,
                'time_slot', OLD.time_slot
            ),
            JSON_OBJECT(
                'status', NEW.status,
                'appointment_date', NEW.appointment_date,
                'doctor_id', NEW.doctor_id,
                'time_slot', NEW.time_slot
            ),
            CONCAT('Appointment updated — status: ', OLD.status, ' -> ', NEW.status)
        );
    END IF;
END $$

DROP TRIGGER IF EXISTS trg_appointment_delete $$
CREATE TRIGGER trg_appointment_delete
BEFORE DELETE ON appointment FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        OLD.booked_by,
        'appointment',
        OLD.appointment_id,
        'DELETE',
        JSON_OBJECT(
            'patient_id', OLD.patient_id,
            'doctor_id', OLD.doctor_id,
            'appointment_date', OLD.appointment_date,
            'status', OLD.status
        ),
        NULL,
        'Appointment deleted'
    );
END $$


-- ============================================================
-- TABLE: visit
-- ============================================================
DROP TRIGGER IF EXISTS trg_visit_insert $$
CREATE TRIGGER trg_visit_insert
AFTER INSERT ON visit FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.doctor_id,
        'visit',
        NEW.visit_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'doctor_id', NEW.doctor_id,
            'visit_date', NEW.visit_date,
            'visit_type', NEW.visit_type,
            'chief_complaint', NEW.chief_complaint
        ),
        'Clinical visit created'
    );
END $$

DROP TRIGGER IF EXISTS trg_visit_update $$
CREATE TRIGGER trg_visit_update
AFTER UPDATE ON visit FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.doctor_id,
        'visit',
        NEW.visit_id,
        'UPDATE',
        JSON_OBJECT(
            'vitals_summary', OLD.vitals_summary,
            'notes', OLD.notes,
            'chief_complaint', OLD.chief_complaint
        ),
        JSON_OBJECT(
            'vitals_summary', NEW.vitals_summary,
            'notes', NEW.notes,
            'chief_complaint', NEW.chief_complaint
        ),
        'Clinical visit updated'
    );
END $$


-- ============================================================
-- TABLE: visit_diagnosis
-- ============================================================
DROP TRIGGER IF EXISTS trg_visit_diagnosis_insert $$
CREATE TRIGGER trg_visit_diagnosis_insert
AFTER INSERT ON visit_diagnosis FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'visit_diagnosis',
        NEW.diagnosis_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'visit_id', NEW.visit_id,
            'diagnosis_code', NEW.diagnosis_code,
            'diagnosis_name', NEW.diagnosis_name,
            'diagnosis_type', NEW.diagnosis_type
        ),
        CONCAT('Diagnosis added: ', NEW.diagnosis_name)
    );
END $$

DROP TRIGGER IF EXISTS trg_visit_diagnosis_delete $$
CREATE TRIGGER trg_visit_diagnosis_delete
BEFORE DELETE ON visit_diagnosis FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'visit_diagnosis',
        OLD.diagnosis_id,
        'DELETE',
        JSON_OBJECT(
            'visit_id', OLD.visit_id,
            'diagnosis_code', OLD.diagnosis_code,
            'diagnosis_name', OLD.diagnosis_name
        ),
        NULL,
        'Diagnosis removed'
    );
END $$


-- ============================================================
-- TABLE: prescription
-- ============================================================
DROP TRIGGER IF EXISTS trg_prescription_insert $$
CREATE TRIGGER trg_prescription_insert
AFTER INSERT ON prescription FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.doctor_id,
        'prescription',
        NEW.prescription_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'doctor_id', NEW.doctor_id,
            'visit_id', NEW.visit_id,
            'prescribed_date', NEW.prescribed_date
        ),
        'Prescription issued'
    );
END $$


-- ============================================================
-- TABLE: prescription_item
-- ============================================================
DROP TRIGGER IF EXISTS trg_prescription_item_insert $$
CREATE TRIGGER trg_prescription_item_insert
AFTER INSERT ON prescription_item FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'prescription_item',
        NEW.item_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'prescription_id', NEW.prescription_id,
            'medicine_name', NEW.medicine_name,
            'dosage', NEW.dosage,
            'frequency', NEW.frequency,
            'duration_days', NEW.duration_days,
            'is_ongoing', NEW.is_ongoing
        ),
        CONCAT('Medication prescribed: ', NEW.medicine_name, ' ', COALESCE(NEW.dosage, ''))
    );
END $$

DROP TRIGGER IF EXISTS trg_prescription_item_update $$
CREATE TRIGGER trg_prescription_item_update
AFTER UPDATE ON prescription_item FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'prescription_item',
        NEW.item_id,
        'UPDATE',
        JSON_OBJECT(
            'medicine_name', OLD.medicine_name,
            'dosage', OLD.dosage,
            'is_ongoing', OLD.is_ongoing
        ),
        JSON_OBJECT(
            'medicine_name', NEW.medicine_name,
            'dosage', NEW.dosage,
            'is_ongoing', NEW.is_ongoing
        ),
        CONCAT('Medication updated: ', NEW.medicine_name)
    );
END $$

DROP TRIGGER IF EXISTS trg_prescription_item_delete $$
CREATE TRIGGER trg_prescription_item_delete
BEFORE DELETE ON prescription_item FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'prescription_item',
        OLD.item_id,
        'DELETE',
        JSON_OBJECT(
            'prescription_id', OLD.prescription_id,
            'medicine_name', OLD.medicine_name,
            'dosage', OLD.dosage
        ),
        NULL,
        CONCAT('Medication removed: ', OLD.medicine_name)
    );
END $$


-- ============================================================
-- TABLE: allergy
-- ============================================================
DROP TRIGGER IF EXISTS trg_allergy_insert $$
CREATE TRIGGER trg_allergy_insert
AFTER INSERT ON allergy FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.recorded_by,
        'allergy',
        NEW.allergy_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'allergen', NEW.allergen,
            'allergy_type', NEW.allergy_type,
            'severity', NEW.severity,
            'reaction', NEW.reaction,
            'status', NEW.status
        ),
        CONCAT('Allergy alert added: ', NEW.allergen, ' (', COALESCE(NEW.severity, 'Unknown severity'), ')')
    );
END $$

DROP TRIGGER IF EXISTS trg_allergy_update $$
CREATE TRIGGER trg_allergy_update
AFTER UPDATE ON allergy FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.recorded_by,
        'allergy',
        NEW.allergy_id,
        'UPDATE',
        JSON_OBJECT(
            'allergen', OLD.allergen,
            'status', OLD.status,
            'severity', OLD.severity
        ),
        JSON_OBJECT(
            'allergen', NEW.allergen,
            'status', NEW.status,
            'severity', NEW.severity
        ),
        CONCAT('Allergy status changed: ', OLD.status, ' -> ', NEW.status)
    );
END $$


-- ============================================================
-- TABLE: patient_condition
-- ============================================================
DROP TRIGGER IF EXISTS trg_patient_condition_insert $$
CREATE TRIGGER trg_patient_condition_insert
AFTER INSERT ON patient_condition FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'patient_condition',
        NEW.condition_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'condition_name', NEW.condition_name,
            'condition_type', NEW.condition_type,
            'status', NEW.status
        ),
        CONCAT('Condition added: ', NEW.condition_name, ' (', COALESCE(NEW.condition_type, 'Unknown'), ')')
    );
END $$

DROP TRIGGER IF EXISTS trg_patient_condition_update $$
CREATE TRIGGER trg_patient_condition_update
AFTER UPDATE ON patient_condition FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
        VALUES (
            NULL,
            'patient_condition',
            NEW.condition_id,
            'UPDATE',
            JSON_OBJECT('condition_name', OLD.condition_name, 'status', OLD.status),
            JSON_OBJECT('condition_name', NEW.condition_name, 'status', NEW.status),
            CONCAT('Condition status: ', OLD.status, ' -> ', NEW.status)
        );
    END IF;
END $$


-- ============================================================
-- TABLE: test_order
-- ============================================================
DROP TRIGGER IF EXISTS trg_test_order_insert $$
CREATE TRIGGER trg_test_order_insert
AFTER INSERT ON test_order FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.ordered_by,
        'test_order',
        NEW.order_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'visit_id', NEW.visit_id,
            'ordered_by', NEW.ordered_by,
            'status', NEW.status,
            'clinical_note', NEW.clinical_note
        ),
        'Lab/diagnostic order placed'
    );
END $$

DROP TRIGGER IF EXISTS trg_test_order_update $$
CREATE TRIGGER trg_test_order_update
AFTER UPDATE ON test_order FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
        VALUES (
            NEW.ordered_by,
            'test_order',
            NEW.order_id,
            'UPDATE',
            JSON_OBJECT('status', OLD.status),
            JSON_OBJECT('status', NEW.status),
            CONCAT('Lab order status: ', OLD.status, ' -> ', NEW.status)
        );
    END IF;
END $$


-- ============================================================
-- TABLE: test_result
-- ============================================================
DROP TRIGGER IF EXISTS trg_test_result_insert $$
CREATE TRIGGER trg_test_result_insert
AFTER INSERT ON test_result FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.verified_by,
        'test_result',
        NEW.result_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'order_item_id', NEW.order_item_id,
            'report_date', NEW.report_date,
            'verification_status', NEW.verification_status,
            'overall_finding', NEW.overall_finding
        ),
        'Diagnostic result published by nurse'
    );
END $$

DROP TRIGGER IF EXISTS trg_test_result_update $$
CREATE TRIGGER trg_test_result_update
AFTER UPDATE ON test_result FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.verified_by,
        'test_result',
        NEW.result_id,
        'UPDATE',
        JSON_OBJECT(
            'verification_status', OLD.verification_status,
            'verified_by', OLD.verified_by,
            'overall_finding', OLD.overall_finding
        ),
        JSON_OBJECT(
            'verification_status', NEW.verification_status,
            'verified_by', NEW.verified_by,
            'overall_finding', NEW.overall_finding
        ),
        CONCAT('Result ', NEW.verification_status, ' — status: ', OLD.verification_status, ' -> ', NEW.verification_status)
    );
END $$


-- ============================================================
-- TABLE: patient_consent
-- ============================================================
DROP TRIGGER IF EXISTS trg_patient_consent_insert $$
CREATE TRIGGER trg_patient_consent_insert
AFTER INSERT ON patient_consent FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'patient_consent',
        NEW.consent_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'hospital_id', NEW.hospital_id,
            'consent_type', NEW.consent_type,
            'status', NEW.status,
            'valid_from', NEW.valid_from,
            'valid_to', NEW.valid_to
        ),
        CONCAT('Consent granted: ', NEW.consent_type)
    );
END $$

DROP TRIGGER IF EXISTS trg_patient_consent_update $$
CREATE TRIGGER trg_patient_consent_update
AFTER UPDATE ON patient_consent FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
        VALUES (
            NULL,
            'patient_consent',
            NEW.consent_id,
            'UPDATE',
            JSON_OBJECT('consent_type', OLD.consent_type, 'status', OLD.status),
            JSON_OBJECT('consent_type', NEW.consent_type, 'status', NEW.status),
            CONCAT('Consent status changed: ', OLD.status, ' -> ', NEW.status)
        );
    END IF;
END $$


-- ============================================================
-- TABLE: medical_document
-- ============================================================
DROP TRIGGER IF EXISTS trg_medical_document_insert $$
CREATE TRIGGER trg_medical_document_insert
AFTER INSERT ON medical_document FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NEW.uploaded_by,
        'medical_document',
        NEW.document_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'title', NEW.title,
            'mime_type', NEW.mime_type,
            'file_size', NEW.file_size,
            'verification_status', NEW.verification_status,
            'uploaded_by', NEW.uploaded_by
        ),
        CONCAT('Document uploaded: ', NEW.title)
    );
END $$

DROP TRIGGER IF EXISTS trg_medical_document_update $$
CREATE TRIGGER trg_medical_document_update
AFTER UPDATE ON medical_document FOR EACH ROW
BEGIN
    IF OLD.verification_status != NEW.verification_status THEN
        INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
        VALUES (
            NEW.uploaded_by,
            'medical_document',
            NEW.document_id,
            'UPDATE',
            JSON_OBJECT('title', OLD.title, 'verification_status', OLD.verification_status),
            JSON_OBJECT('title', NEW.title, 'verification_status', NEW.verification_status),
            CONCAT('Document verification: ', OLD.verification_status, ' -> ', NEW.verification_status)
        );
    END IF;
END $$


-- ============================================================
-- TABLE: medical_summary
-- ============================================================
DROP TRIGGER IF EXISTS trg_medical_summary_insert $$
CREATE TRIGGER trg_medical_summary_insert
AFTER INSERT ON medical_summary FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'medical_summary',
        NEW.summary_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'appointment_id', NEW.appointment_id,
            'summary_type', NEW.summary_type,
            'generated_by', NEW.generated_by,
            'version_no', NEW.version_no
        ),
        CONCAT('Medical summary generated: type=', NEW.summary_type, ', version=', NEW.version_no)
    );
END $$

DROP TRIGGER IF EXISTS trg_medical_summary_update $$
CREATE TRIGGER trg_medical_summary_update
AFTER UPDATE ON medical_summary FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
    VALUES (
        NULL,
        'medical_summary',
        NEW.summary_id,
        'UPDATE',
        JSON_OBJECT('summary_type', OLD.summary_type, 'is_current', OLD.is_current, 'version_no', OLD.version_no),
        JSON_OBJECT('summary_type', NEW.summary_type, 'is_current', NEW.is_current, 'version_no', NEW.version_no),
        CONCAT('Summary updated: is_current=', NEW.is_current)
    );
END $$


-- ============================================================
-- TABLE: user_account (login security tracking)
-- ============================================================
DROP TRIGGER IF EXISTS trg_user_account_update $$
CREATE TRIGGER trg_user_account_update
AFTER UPDATE ON user_account FOR EACH ROW
BEGIN
    IF OLD.last_login != NEW.last_login OR (OLD.last_login IS NULL AND NEW.last_login IS NOT NULL) THEN
        INSERT INTO audit_trail (user_id, table_name, record_id, action_type, old_value, new_value, remarks)
        VALUES (
            NEW.user_id,
            'user_account',
            NEW.user_id,
            'UPDATE',
            JSON_OBJECT('last_login', OLD.last_login, 'is_active', OLD.is_active),
            JSON_OBJECT('last_login', NEW.last_login, 'is_active', NEW.is_active),
            'User login recorded'
        );
    END IF;
END $$

DELIMITER ;

-- Verify all triggers were created
SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_TIMING
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'patient_record_system'
ORDER BY EVENT_OBJECT_TABLE, ACTION_TIMING;


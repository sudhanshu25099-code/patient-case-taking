-- 04_logging_schema.sql
-- Notifications & Logging (9)
-- Run order: run after 03

USE patient_record_system;

-- =====================================================================
-- 9. NOTIFICATIONS & LOGGING
-- =====================================================================

CREATE TABLE notification (
    notification_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id            INT UNSIGNED NOT NULL,
    appointment_id     INT UNSIGNED NULL,               -- NEW
    title              VARCHAR(200) NOT NULL,
    message            TEXT,
    type               ENUM('Appointment','Consent','System','Other') NOT NULL DEFAULT 'System',
    is_read            BOOLEAN NOT NULL DEFAULT FALSE,
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_notif_user (user_id, is_read),
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id)        REFERENCES user_account(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_appt FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE access_log (
    log_id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id            INT UNSIGNED NOT NULL,
    patient_id         INT UNSIGNED NOT NULL,
    document_id        INT UNSIGNED NULL,
    action_type        ENUM('VIEW','LOGIN','UPLOAD','CONSENT','OTHER') NOT NULL,
    action_time        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address         VARCHAR(45),
    remarks            VARCHAR(255),
    KEY idx_alog_patient (patient_id, action_time),
    KEY idx_alog_user (user_id, action_time),
    CONSTRAINT fk_alog_user    FOREIGN KEY (user_id)     REFERENCES user_account(user_id),
    CONSTRAINT fk_alog_patient FOREIGN KEY (patient_id)  REFERENCES patient_profile(patient_id),
    CONSTRAINT fk_alog_doc     FOREIGN KEY (document_id) REFERENCES medical_document(document_id)
) ENGINE=InnoDB;

CREATE TABLE audit_trail (
    audit_id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id            INT UNSIGNED NULL,
    table_name         VARCHAR(80) NOT NULL,
    record_id          VARCHAR(40) NOT NULL,
    action_type        ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    old_value          JSON NULL,
    new_value          JSON NULL,
    action_time        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks            VARCHAR(255),
    KEY idx_audit_table (table_name, record_id),
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES user_account(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;
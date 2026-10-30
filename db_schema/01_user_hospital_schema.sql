-- 01_user_hospital_schema.sql
-- Database + Identity (section 1) + Hospital (section 2)
-- Run order: run this FIRST

DROP DATABASE IF EXISTS patient_record_system;
CREATE DATABASE patient_record_system
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE patient_record_system;

-- =====================================================================
-- 1. USER & IDENTITY MANAGEMENT
-- =====================================================================

CREATE TABLE person (
    person_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name          VARCHAR(150) NOT NULL,
    date_of_birth      DATE,
    gender             ENUM('Male','Female','Other') ,
    phone              VARCHAR(20),
    email              VARCHAR(150),
    address            VARCHAR(255),
    city               VARCHAR(100),
    state              VARCHAR(100),
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_person_email (email),
    KEY idx_person_phone (phone)
) ENGINE=InnoDB;

CREATE TABLE role (
    role_id            SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    role_name          VARCHAR(50) NOT NULL,
    UNIQUE KEY uq_role_name (role_name)
) ENGINE=InnoDB;

CREATE TABLE user_account (
    user_id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    person_id          INT UNSIGNED NOT NULL,
    username           VARCHAR(60)  NOT NULL,
    email              VARCHAR(150) NOT NULL,
    password_hash      VARCHAR(255) NOT NULL,
    is_active          BOOLEAN NOT NULL DEFAULT TRUE,
    last_login         DATETIME NULL,
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_person   (person_id),            -- Person 1 : 0..1 UserAccount
    UNIQUE KEY uq_user_username (username),
    UNIQUE KEY uq_user_email    (email),
    CONSTRAINT fk_user_person FOREIGN KEY (person_id) REFERENCES person(person_id)
) ENGINE=InnoDB;

CREATE TABLE user_role (                                -- User M : N Role
    user_id            INT UNSIGNED NOT NULL,
    role_id            SMALLINT UNSIGNED NOT NULL,
    assigned_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_ur_user FOREIGN KEY (user_id) REFERENCES user_account(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ur_role FOREIGN KEY (role_id) REFERENCES role(role_id)
) ENGINE=InnoDB;

-- =====================================================================
-- 2. HOSPITAL MANAGEMENT
-- =====================================================================

CREATE TABLE hospital (
    hospital_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(200) NOT NULL,
    registration_no    VARCHAR(80)  NOT NULL,
    address            VARCHAR(255),
    city               VARCHAR(100),
    state              VARCHAR(100),
    contact_no         VARCHAR(20),
    email              VARCHAR(150),
    UNIQUE KEY uq_hospital_reg (registration_no)
) ENGINE=InnoDB;

CREATE TABLE department (
    department_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    hospital_id        INT UNSIGNED NOT NULL,
    name               VARCHAR(120) NOT NULL,
    description        VARCHAR(255),
    UNIQUE KEY uq_dept_hospital_name (hospital_id, name),
    CONSTRAINT fk_dept_hospital FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
) ENGINE=InnoDB;

-- Profiles (specialization of PERSON; a person can hold more than one) ----

CREATE TABLE patient_profile (
    patient_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    person_id          INT UNSIGNED NOT NULL,
    blood_group        ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-') NULL,
    emergency_contact_name  VARCHAR(150),
    emergency_contact_phone VARCHAR(20),
    abha_linked        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_patient_person (person_id),
    CONSTRAINT fk_patient_person FOREIGN KEY (person_id) REFERENCES person(person_id)
) ENGINE=InnoDB;

CREATE TABLE doctor_profile (
    doctor_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    person_id          INT UNSIGNED NOT NULL,
    license_no         VARCHAR(60)  NOT NULL,
    qualification      VARCHAR(200),
    specialization     VARCHAR(120),
    experience_years   TINYINT UNSIGNED,
    consultation_fee   DECIMAL(10,2),
    UNIQUE KEY uq_doctor_person  (person_id),
    UNIQUE KEY uq_doctor_license (license_no),
    CONSTRAINT fk_doctor_person FOREIGN KEY (person_id) REFERENCES person(person_id)
) ENGINE=InnoDB;

CREATE TABLE nurse_profile (
    nurse_id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    person_id          INT UNSIGNED NOT NULL,
    department_id      INT UNSIGNED NULL,
    employee_no        VARCHAR(60) NOT NULL,
    shift              ENUM('Morning','Evening','Night') NULL,
    UNIQUE KEY uq_nurse_person (person_id),
    UNIQUE KEY uq_nurse_emp    (employee_no),
    CONSTRAINT fk_nurse_person FOREIGN KEY (person_id)     REFERENCES person(person_id),
    CONSTRAINT fk_nurse_dept   FOREIGN KEY (department_id) REFERENCES department(department_id)
) ENGINE=InnoDB;

-- NEW: a doctor can work in many hospitals / departments
CREATE TABLE doctor_hospital (
    doctor_id          INT UNSIGNED NOT NULL,
    hospital_id        INT UNSIGNED NOT NULL,
    department_id      INT UNSIGNED NULL,
    joined_date        DATE,
    is_active          BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (doctor_id, hospital_id),
    CONSTRAINT fk_dh_doctor   FOREIGN KEY (doctor_id)     REFERENCES doctor_profile(doctor_id),
    CONSTRAINT fk_dh_hospital FOREIGN KEY (hospital_id)   REFERENCES hospital(hospital_id),
    CONSTRAINT fk_dh_dept     FOREIGN KEY (department_id) REFERENCES department(department_id)
) ENGINE=InnoDB;
import json
from sqlalchemy import text
from sqlalchemy.engine import Connection


# ---------- PERSON ----------
PERSON_COLS = ("person_id, full_name, date_of_birth, gender, phone, email, "
               "address, city, state, created_at")


def create_person(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO person (full_name, date_of_birth, gender, phone, email,
                            address, city, state)
        VALUES (:full_name, :date_of_birth, :gender, :phone, :email,
                :address, :city, :state)
    """)
    return conn.execute(sql, d).lastrowid


def get_person(conn: Connection, person_id: int):
    return conn.execute(
        text(f"SELECT {PERSON_COLS} FROM person WHERE person_id = :id"),
        {"id": person_id},
    ).mappings().first()


def list_persons(conn: Connection, limit: int = 100, offset: int = 0):
    return conn.execute(
        text(f"SELECT {PERSON_COLS} FROM person ORDER BY person_id LIMIT :l OFFSET :o"),
        {"l": limit, "o": offset},
    ).mappings().all()


def update_person(conn: Connection, person_id: int, d: dict) -> int:
    sql = text("""
        UPDATE person SET full_name = :full_name, date_of_birth = :date_of_birth,
            gender = :gender, phone = :phone, email = :email,
            address = :address, city = :city, state = :state
        WHERE person_id = :id
    """)
    d["id"] = person_id
    return conn.execute(sql, d).rowcount


def delete_person(conn: Connection, person_id: int) -> int:
    return conn.execute(
        text("DELETE FROM person WHERE person_id = :id"), {"id": person_id}
    ).rowcount


# ---------- USER ACCOUNT ----------
def create_user(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO user_account (person_id, username, email, password_hash, is_active)
        VALUES (:person_id, :username, :email, :password_hash, :is_active)
    """)
    return conn.execute(sql, d).lastrowid


def get_user(conn: Connection, user_id: int):
    return conn.execute(text("""
        SELECT user_id, person_id, username, email, is_active, last_login, created_at
        FROM user_account WHERE user_id = :id
    """), {"id": user_id}).mappings().first()


def get_user_by_username(conn: Connection, username: str):
    return conn.execute(text("""
        SELECT user_id, person_id, username, email, password_hash, is_active
        FROM user_account WHERE username = :u
    """), {"u": username}).mappings().first()


# ---------- ROLES ----------
def create_role(conn: Connection, role_name: str) -> int:
    return conn.execute(
        text("INSERT INTO role (role_name) VALUES (:n)"), {"n": role_name}
    ).lastrowid


def list_roles(conn: Connection):
    return conn.execute(
        text("SELECT role_id, role_name FROM role ORDER BY role_id")
    ).mappings().all()


def assign_role(conn: Connection, user_id: int, role_id: int):
    conn.execute(
        text("INSERT INTO user_role (user_id, role_id) VALUES (:u, :r)"),
        {"u": user_id, "r": role_id},
    )


def user_roles(conn: Connection, user_id: int):
    return conn.execute(text("""
        SELECT r.role_id, r.role_name
        FROM role r JOIN user_role ur ON ur.role_id = r.role_id
        WHERE ur.user_id = :u
    """), {"u": user_id}).mappings().all()


# ---------- PROFILES ----------
def create_patient(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO patient_profile
            (person_id, blood_group, emergency_contact_name,
             emergency_contact_phone, abha_linked)
        VALUES (:person_id, :blood_group, :emergency_contact_name,
                :emergency_contact_phone, :abha_linked)
    """)
    return conn.execute(sql, d).lastrowid


def get_patient(conn: Connection, patient_id: int):
    return conn.execute(text("""
        SELECT patient_id, person_id, blood_group, emergency_contact_name,
               emergency_contact_phone, abha_linked, created_at
        FROM patient_profile WHERE patient_id = :id
    """), {"id": patient_id}).mappings().first()


def create_doctor(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO doctor_profile
            (person_id, license_no, qualification, specialization,
             experience_years, consultation_fee)
        VALUES (:person_id, :license_no, :qualification, :specialization,
                :experience_years, :consultation_fee)
    """)
    return conn.execute(sql, d).lastrowid


def get_doctor(conn: Connection, doctor_id: int):
    return conn.execute(text("""
        SELECT doctor_id, person_id, license_no, qualification, specialization,
               experience_years, consultation_fee
        FROM doctor_profile WHERE doctor_id = :id
    """), {"id": doctor_id}).mappings().first()


def create_nurse(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO nurse_profile (person_id, department_id, employee_no, shift)
        VALUES (:person_id, :department_id, :employee_no, :shift)
    """)
    return conn.execute(sql, d).lastrowid


def get_nurse(conn: Connection, nurse_id: int):
    return conn.execute(text("""
        SELECT nurse_id, person_id, department_id, employee_no, shift
        FROM nurse_profile WHERE nurse_id = :id
    """), {"id": nurse_id}).mappings().first()
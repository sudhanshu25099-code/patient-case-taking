from sqlalchemy import text
from sqlalchemy.engine import Connection


HOSP_COLS = "hospital_id, name, registration_no, address, city, state, contact_no, email"


def create_hospital(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO hospital (name, registration_no, address, city, state, contact_no, email)
        VALUES (:name, :registration_no, :address, :city, :state, :contact_no, :email)
    """)
    return conn.execute(sql, d).lastrowid


def get_hospital(conn: Connection, hospital_id: int):
    return conn.execute(
        text(f"SELECT {HOSP_COLS} FROM hospital WHERE hospital_id = :id"),
        {"id": hospital_id},
    ).mappings().first()


def list_hospitals(conn: Connection, limit: int = 100, offset: int = 0):
    return conn.execute(
        text(f"SELECT {HOSP_COLS} FROM hospital ORDER BY hospital_id LIMIT :l OFFSET :o"),
        {"l": limit, "o": offset},
    ).mappings().all()


def update_hospital(conn: Connection, hospital_id: int, d: dict) -> int:
    sql = text("""
        UPDATE hospital SET name = :name, registration_no = :registration_no,
            address = :address, city = :city, state = :state,
            contact_no = :contact_no, email = :email
        WHERE hospital_id = :id
    """)
    d["id"] = hospital_id
    return conn.execute(sql, d).rowcount


def delete_hospital(conn: Connection, hospital_id: int) -> int:
    return conn.execute(
        text("DELETE FROM hospital WHERE hospital_id = :id"), {"id": hospital_id}
    ).rowcount


# ---------- DEPARTMENTS ----------
def create_department(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO department (hospital_id, name, description)
        VALUES (:hospital_id, :name, :description)
    """)
    return conn.execute(sql, d).lastrowid


def list_departments(conn: Connection, hospital_id: int):
    return conn.execute(text("""
        SELECT department_id, hospital_id, name, description
        FROM department WHERE hospital_id = :h
    """), {"h": hospital_id}).mappings().all()


def link_doctor_hospital(conn: Connection, d: dict):
    conn.execute(text("""
        INSERT INTO doctor_hospital
            (doctor_id, hospital_id, department_id, joined_date, is_active)
        VALUES (:doctor_id, :hospital_id, :department_id, :joined_date, :is_active)
        ON DUPLICATE KEY UPDATE
            department_id = COALESCE(:department_id, doctor_hospital.department_id),
            joined_date = :joined_date,
            is_active = :is_active
    """), d)


def doctors_in_hospital(conn: Connection, hospital_id: int):
    return conn.execute(text("""
        SELECT dh.doctor_id, p.full_name, dp.specialization,
               dh.department_id, dh.is_active
        FROM doctor_hospital dh
        JOIN doctor_profile dp ON dp.doctor_id = dh.doctor_id
        JOIN person p          ON p.person_id   = dp.person_id
        WHERE dh.hospital_id = :h
    """), {"h": hospital_id}).mappings().all()


def list_all_doctor_affiliations(conn: Connection):
    return conn.execute(text("""
        SELECT dh.doctor_id, dh.hospital_id, p.full_name as doctor_name, dp.specialization,
               h.name as hospital_name, d.name as department_name, dh.joined_date, dh.is_active
        FROM doctor_hospital dh
        JOIN doctor_profile dp ON dp.doctor_id = dh.doctor_id
        JOIN person p          ON p.person_id   = dp.person_id
        JOIN hospital h        ON h.hospital_id = dh.hospital_id
        LEFT JOIN department d ON d.department_id = dh.department_id
        ORDER BY h.name, p.full_name
    """)).mappings().all()

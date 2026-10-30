from sqlalchemy import text
from sqlalchemy.engine import Connection


def create_hospital(conn: Connection, d: dict) -> int:
    sql = text("""
        INSERT INTO hospital (name, registration_no, address, city, state,
                              contact_no, email)
        VALUES (:name, :registration_no, :address, :city, :state,
                :contact_no, :email)
    """)
    return conn.execute(sql, d).lastrowid


def get_hospital(conn: Connection, hospital_id: int):
    return conn.execute(text("""
        SELECT hospital_id, name, registration_no, address, city, state,
               contact_no, email
        FROM hospital WHERE hospital_id = :id
    """), {"id": hospital_id}).mappings().first()


def list_hospitals(conn: Connection, limit: int = 100, offset: int = 0):
    return conn.execute(text("""
        SELECT hospital_id, name, registration_no, address, city, state,
               contact_no, email
        FROM hospital ORDER BY hospital_id LIMIT :l OFFSET :o
    """), {"l": limit, "o": offset}).mappings().all()


def create_department(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO department (hospital_id, name, description)
        VALUES (:hospital_id, :name, :description)
    """), d).lastrowid


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
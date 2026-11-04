from sqlalchemy import text
from sqlalchemy.engine import Connection


def create_test(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO diagnostic_test (test_name, category, description)
        VALUES (:test_name, :category, :description)
    """), d).lastrowid


def list_tests(conn: Connection):
    return conn.execute(text("""
        SELECT test_id, test_name, category, description
        FROM diagnostic_test ORDER BY test_id
    """)).mappings().all()


def create_parameter(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO test_parameter
            (test_id, parameter_name, unit, reference_range)
        VALUES (:test_id, :parameter_name, :unit, :reference_range)
    """), d).lastrowid


def list_parameters(conn: Connection, test_id: int):
    return conn.execute(text("""
        SELECT parameter_id, test_id, parameter_name, unit, reference_range
        FROM test_parameter WHERE test_id = :t
    """), {"t": test_id}).mappings().all()


def create_order(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO test_order
            (visit_id, ordered_by, status, clinical_note)
        VALUES (:visit_id, :ordered_by, :status, :clinical_note)
    """), d).lastrowid


def get_order(conn: Connection, order_id: int):
    return conn.execute(text("""
        SELECT order_id, visit_id, ordered_by, order_date, status, clinical_note
        FROM test_order WHERE order_id = :id
    """), {"id": order_id}).mappings().first()


def add_order_item(conn: Connection, order_id: int, test_id: int) -> int:
    return conn.execute(text("""
        INSERT INTO test_order_item (order_id, test_id, status)
        VALUES (:o, :t, 'Pending')
    """), {"o": order_id, "t": test_id}).lastrowid


def list_order_items(conn: Connection, order_id: int):
    return conn.execute(text("""
        SELECT order_item_id, order_id, test_id, status
        FROM test_order_item WHERE order_id = :o
    """), {"o": order_id}).mappings().all()


def list_orders_by_visit(conn, v): 
    return conn.execute(text("""
        SELECT * FROM test_order WHERE visit_id=:v
    """), {"v": v}).mappings().all()


def create_result(conn: Connection, d: dict) -> int:
    d = dict(d)
    d.setdefault("verified_by", None)
    d.setdefault("verification_status", "Pending")

    existing = conn.execute(text("""
        SELECT result_id FROM test_result WHERE order_item_id = :order_item_id
    """), {"order_item_id": d["order_item_id"]}).mappings().first()

    if existing:
        conn.execute(text("""
            UPDATE test_result
            SET report_date = :report_date,
                overall_finding = :overall_finding,
                verification_status = :verification_status,
                verified_by = :verified_by
            WHERE order_item_id = :order_item_id
        """), d)
        rid = existing["result_id"]
    else:
        rid = conn.execute(text("""
            INSERT INTO test_result
                (order_item_id, report_date, overall_finding,
                 verified_by, verification_status)
            VALUES
                (:order_item_id, :report_date, :overall_finding,
                 :verified_by, :verification_status)
        """), d).lastrowid

    # Mark the individual order item as Completed
    conn.execute(text("""
        UPDATE test_order_item SET status = 'Completed' WHERE order_item_id = :id
    """), {"id": d["order_item_id"]})

    # Check if all items in parent test_order are Completed
    parent = conn.execute(text("""
        SELECT order_id FROM test_order_item WHERE order_item_id = :id
    """), {"id": d["order_item_id"]}).mappings().first()
    if parent:
        pending_count = conn.execute(text("""
            SELECT COUNT(*) FROM test_order_item WHERE order_id = :oid AND status = 'Pending'
        """), {"oid": parent["order_id"]}).scalar()
        if pending_count == 0:
            conn.execute(text("""
                UPDATE test_order SET status = 'Completed' WHERE order_id = :oid
            """), {"oid": parent["order_id"]})

    return rid


def add_result_item(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO test_result_item
            (result_id, parameter_id, result_value, flag, notes)
        VALUES (:result_id, :parameter_id, :result_value, :flag, :notes)
    """), d).lastrowid


def get_result(conn: Connection, result_id: int):
    return conn.execute(text("""
        SELECT result_id, order_item_id, report_date, overall_finding,
               verified_by, verification_status
        FROM test_result WHERE result_id = :id
    """), {"id": result_id}).mappings().first()


def list_result_items(conn: Connection, result_id: int):
    return conn.execute(text("""
        SELECT result_item_id, result_id, parameter_id, result_value, flag, notes
        FROM test_result_item WHERE result_id = :r
    """), {"r": result_id}).mappings().all()


def list_all_orders(conn: Connection):
    return conn.execute(text("""
        SELECT o.order_id, o.visit_id, o.ordered_by, o.status, o.order_date, o.clinical_note,
               p.full_name as doctor_name
        FROM test_order o
        LEFT JOIN doctor_profile d ON o.ordered_by = d.doctor_id
        LEFT JOIN person p ON d.person_id = p.person_id
        ORDER BY o.order_id DESC
    """)).mappings().all()


def list_results(conn: Connection):
    return conn.execute(text("""
        SELECT r.result_id, r.order_item_id, r.report_date, r.overall_finding,
               r.verified_by, r.verification_status,
               t.test_name
        FROM test_result r
        LEFT JOIN test_order_item oi ON r.order_item_id = oi.order_item_id
        LEFT JOIN diagnostic_test t ON oi.test_id = t.test_id
        ORDER BY r.result_id DESC
    """)).mappings().all()


def list_all_order_items(conn: Connection):
    return conn.execute(text("""
        SELECT oi.order_item_id, oi.order_id, oi.test_id, oi.status as item_status,
               t.test_name, t.category,
               o.visit_id, o.order_date, o.status as order_status, o.clinical_note,
               per.full_name as patient_name, doc_per.full_name as doctor_name,
               tr.result_id, tr.overall_finding, tr.verification_status
        FROM test_order_item oi
        JOIN test_order o ON oi.order_id = o.order_id
        JOIN diagnostic_test t ON oi.test_id = t.test_id
        LEFT JOIN visit v ON o.visit_id = v.visit_id
        LEFT JOIN patient_profile pp ON v.patient_id = pp.patient_id
        LEFT JOIN person per ON pp.person_id = per.person_id
        LEFT JOIN doctor_profile d ON o.ordered_by = d.doctor_id
        LEFT JOIN person doc_per ON d.person_id = doc_per.person_id
        LEFT JOIN test_result tr ON oi.order_item_id = tr.order_item_id
        ORDER BY oi.order_item_id DESC
    """)).mappings().all()

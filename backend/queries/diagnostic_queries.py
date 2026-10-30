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
    return conn.execute(text("""
        INSERT INTO test_result
            (order_item_id, report_date, overall_finding,
             verified_by, verification_status)
        VALUES
            (:order_item_id, :report_date, :overall_finding,
             :verified_by, :verification_status)
    """), d).lastrowid


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


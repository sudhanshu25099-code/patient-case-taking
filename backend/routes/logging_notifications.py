from fastapi import APIRouter, Depends, Query
from sqlalchemy.engine import Connection
from sqlalchemy import text
from typing import Optional

from dependencies import get_db_connection
from queries import logging_queries as q
from schemas.logging_notifications import (
    NotificationCreate, NotificationOut,
    AccessLogCreate, AccessLogOut,
    AuditTrailCreate, AuditTrailOut,
)

router = APIRouter(prefix="/logs", tags=["logging"])


@router.post("/notifications", response_model=NotificationOut, status_code=201)
def create_notif(p: NotificationCreate,
                 conn: Connection = Depends(get_db_connection)):
    nid = q.create_notification(conn, p.model_dump())
    return q.get_notification(conn, nid)


@router.get("/notifications/{user_id}", response_model=list[NotificationOut])
def list_notif(user_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_notifications(conn, user_id)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, conn: Connection = Depends(get_db_connection)):
    q.mark_read(conn, notification_id)
    return q.get_notification(conn, notification_id)


@router.post("/access", response_model=AccessLogOut, status_code=201)
def create_alog(p: AccessLogCreate, conn: Connection = Depends(get_db_connection)):
    lid = q.create_access_log(conn, p.model_dump())
    return q.get_access_log(conn, lid)


@router.get("/access/user/{user_id}", response_model=list[AccessLogOut])
def user_alogs(user_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_access_logs(conn, user_id)


@router.get("/access/all")
def all_access_logs(limit: int = Query(200, le=1000), conn: Connection = Depends(get_db_connection)):
    rows = conn.execute(text("""
        SELECT al.log_id, al.user_id, ua.username, per.full_name as user_name,
               al.patient_id, pp.full_name as patient_name,
               al.document_id, al.action_type, al.action_time,
               al.ip_address, al.remarks
        FROM access_log al
        LEFT JOIN user_account ua ON al.user_id = ua.user_id
        LEFT JOIN person per ON ua.person_id = per.person_id
        LEFT JOIN patient_profile pt ON al.patient_id = pt.patient_id
        LEFT JOIN person pp ON pt.person_id = pp.person_id
        ORDER BY al.action_time DESC
        LIMIT :lim
    """), {"lim": limit}).mappings().all()
    return [dict(r) for r in rows]


@router.post("/audit", response_model=AuditTrailOut, status_code=201)
def create_audit(p: AuditTrailCreate, conn: Connection = Depends(get_db_connection)):
    aid = q.create_audit(conn, p.model_dump())
    return q.get_audit(conn, aid)


@router.get("/audit/tables")
def list_audited_tables(conn: Connection = Depends(get_db_connection)):
    """Return all distinct table names present in audit_trail."""
    rows = conn.execute(text("""
        SELECT DISTINCT table_name, COUNT(*) as record_count
        FROM audit_trail
        GROUP BY table_name
        ORDER BY table_name
    """)).mappings().all()
    return [dict(r) for r in rows]


@router.get("/audit/{table_name}")
def audit_for_table(
    table_name: str,
    action_type: Optional[str] = Query(None),
    limit: int = Query(200, le=2000),
    conn: Connection = Depends(get_db_connection)
):
    """Get audit trail for a specific table, optionally filtered by action type."""
    base_query = """
        SELECT at.audit_id, at.user_id,
               COALESCE(per.full_name, CONCAT('User #', at.user_id)) as user_name,
               ua.username,
               at.table_name, at.record_id, at.action_type,
               at.old_value, at.new_value,
               at.action_time, at.remarks
        FROM audit_trail at
        LEFT JOIN user_account ua ON at.user_id = ua.user_id
        LEFT JOIN person per ON ua.person_id = per.person_id
        WHERE at.table_name = :t
    """
    params = {"t": table_name, "lim": limit}
    if action_type:
        base_query += " AND at.action_type = :act"
        params["act"] = action_type
    base_query += " ORDER BY at.action_time DESC LIMIT :lim"

    rows = conn.execute(text(base_query), params).mappings().all()
    return [dict(r) for r in rows]


@router.get("/audit-summary")
def audit_summary(conn: Connection = Depends(get_db_connection)):
    """High-level statistics for the audit trail dashboard."""
    stats = conn.execute(text("""
        SELECT
            COUNT(*) as total_events,
            SUM(action_type = 'INSERT') as inserts,
            SUM(action_type = 'UPDATE') as updates,
            SUM(action_type = 'DELETE') as deletes,
            COUNT(DISTINCT table_name) as tables_monitored,
            COUNT(DISTINCT user_id) as unique_users,
            MIN(action_time) as earliest_event,
            MAX(action_time) as latest_event
        FROM audit_trail
    """)).mappings().first()

    by_table = conn.execute(text("""
        SELECT table_name, action_type, COUNT(*) as cnt
        FROM audit_trail
        GROUP BY table_name, action_type
        ORDER BY table_name, action_type
    """)).mappings().all()

    recent = conn.execute(text("""
        SELECT at.audit_id, at.table_name, at.record_id, at.action_type,
               COALESCE(per.full_name, CONCAT('User #', at.user_id)) as user_name,
               at.action_time, at.remarks
        FROM audit_trail at
        LEFT JOIN user_account ua ON at.user_id = ua.user_id
        LEFT JOIN person per ON ua.person_id = per.person_id
        ORDER BY at.action_time DESC LIMIT 20
    """)).mappings().all()

    return {
        "stats": dict(stats) if stats else {},
        "by_table": [dict(r) for r in by_table],
        "recent_activity": [dict(r) for r in recent],
    }


@router.get("/access/patient/{patient_id}")
def audit_patient_access(patient_id: int, conn: Connection = Depends(get_db_connection)):
    rows = conn.execute(text("""
        SELECT al.log_id, al.user_id, ua.username,
               COALESCE(per.full_name, CONCAT('User #', al.user_id)) as user_name,
               al.action_type, al.action_time, al.ip_address, al.remarks
        FROM access_log al
        LEFT JOIN user_account ua ON al.user_id = ua.user_id
        LEFT JOIN person per ON ua.person_id = per.person_id
        WHERE al.patient_id = :p ORDER BY al.action_time DESC
    """), {"p": patient_id}).mappings().all()
    return [dict(r) for r in rows]


@router.get("/db/processlist")
def running_queries(conn: Connection = Depends(get_db_connection)):
    rows = conn.execute(text("""
        SELECT ID as thread_id, USER as db_user, HOST as host, DB as db_name,
               COMMAND as command, TIME as time_seconds, STATE as state, INFO as query
        FROM information_schema.PROCESSLIST
        ORDER BY TIME DESC
    """)).mappings().all()
    return [dict(r) for r in rows]


@router.get("/db/queries")
def recent_queries(
    join_only: bool = False,
    limit: int = Query(50, le=200),
    conn: Connection = Depends(get_db_connection)
):
    """Fetch recent SQL queries executed against the DB from performance_schema."""
    try:
        # Ensure consumer is enabled
        conn.execute(text("UPDATE performance_schema.setup_consumers SET ENABLED='YES' WHERE NAME='events_statements_history_long'"))
        
        sql = """
            SELECT
                EVENT_ID as event_id,
                SQL_TEXT as query,
                ROUND(TIMER_WAIT / 1000000000, 3) as latency_ms,
                ROWS_EXAMINED as rows_examined,
                ROWS_SENT as rows_sent,
                ERRORS as errors,
                CASE WHEN UPPER(SQL_TEXT) LIKE '%JOIN%' THEN 1 ELSE 0 END as has_join,
                CURRENT_SCHEMA as db_name
            FROM performance_schema.events_statements_history_long
            WHERE SQL_TEXT IS NOT NULL
              AND SQL_TEXT NOT LIKE '%performance_schema%'
              AND SQL_TEXT NOT LIKE '%events_statements%'
              AND SQL_TEXT NOT LIKE '%PROCESSLIST%'
              AND SQL_TEXT NOT LIKE 'SET %'
              AND SQL_TEXT NOT LIKE 'SHOW %'
        """
        if join_only:
            sql += " AND UPPER(SQL_TEXT) LIKE '%JOIN%'"
        sql += " ORDER BY EVENT_ID DESC LIMIT :lim"
        
        rows = conn.execute(text(sql), {"lim": limit}).mappings().all()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"query": f"Query history unavailable: {str(e)}", "latency_ms": 0, "rows_examined": 0, "rows_sent": 0, "has_join": 0}]


@router.get("/db/digest")
def query_digest(
    join_only: bool = False,
    limit: int = Query(50, le=200),
    conn: Connection = Depends(get_db_connection)
):
    """Fetch aggregated query statement statistics (template, execution count, latency) from performance_schema."""
    try:
        sql = """
            SELECT
                DIGEST_TEXT as query_template,
                COUNT_STAR as exec_count,
                ROUND(AVG_TIMER_WAIT / 1000000000, 3) as avg_latency_ms,
                ROUND(MAX_TIMER_WAIT / 1000000000, 3) as max_latency_ms,
                SUM_ROWS_EXAMINED as total_rows_examined,
                SUM_ROWS_SENT as total_rows_sent,
                LAST_SEEN as last_executed,
                CASE WHEN UPPER(DIGEST_TEXT) LIKE '%JOIN%' THEN 1 ELSE 0 END as has_join
            FROM performance_schema.events_statements_summary_by_digest
            WHERE DIGEST_TEXT IS NOT NULL
              AND DIGEST_TEXT NOT LIKE '%performance_schema%'
              AND DIGEST_TEXT NOT LIKE '%setup_%'
              AND DIGEST_TEXT NOT LIKE 'SET %'
              AND DIGEST_TEXT NOT LIKE 'SHOW %'
              AND (SCHEMA_NAME = 'patient_record_system' OR SCHEMA_NAME IS NULL)
        """
        if join_only:
            sql += " AND UPPER(DIGEST_TEXT) LIKE '%JOIN%'"
        sql += " ORDER BY LAST_SEEN DESC LIMIT :lim"
        
        rows = conn.execute(text(sql), {"lim": limit}).mappings().all()
        return [dict(r) for r in rows]
    except Exception as e:
        return []



@router.get("/db/triggers")
def get_triggers(conn: Connection = Depends(get_db_connection)):
    """List all audit triggers configured in MySQL directly from information_schema."""
    rows = conn.execute(text("""
        SELECT TRIGGER_NAME as name, EVENT_MANIPULATION as event,
               EVENT_OBJECT_TABLE as table_name, ACTION_TIMING as timing
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = 'patient_record_system'
        ORDER BY EVENT_OBJECT_TABLE, ACTION_TIMING
    """)).mappings().all()
    return [dict(r) for r in rows]

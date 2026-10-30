from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection

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


@router.post("/audit", response_model=AuditTrailOut, status_code=201)
def create_audit(p: AuditTrailCreate, conn: Connection = Depends(get_db_connection)):
    aid = q.create_audit(conn, p.model_dump())
    return q.get_audit(conn, aid)


@router.get("/audit/{table_name}", response_model=list[AuditTrailOut])
def audit_for_table(table_name: str, conn: Connection = Depends(get_db_connection)):
    return q.list_audit_for_table(conn, table_name)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import diagnostic_queries as q
from schemas.diagnostics import (
    DiagnosticTestCreate, DiagnosticTestOut,
    TestParameterCreate, TestParameterOut,
    TestOrderCreate, TestOrderOut, TestOrderItemOut,
    TestResultCreate, TestResultOut,
)

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.post("/tests", response_model=DiagnosticTestOut, status_code=201)
def create_test(p: DiagnosticTestCreate, conn: Connection = Depends(get_db_connection)):
    tid = q.create_test(conn, p.model_dump())
    return {**p.model_dump(), "test_id": tid}


@router.get("/tests", response_model=list[DiagnosticTestOut])
def list_tests(conn: Connection = Depends(get_db_connection)):
    return q.list_tests(conn)


@router.post("/parameters", response_model=TestParameterOut, status_code=201)
def create_param(p: TestParameterCreate, conn: Connection = Depends(get_db_connection)):
    pid = q.create_parameter(conn, p.model_dump())
    return {**p.model_dump(), "parameter_id": pid}


@router.get("/tests/{test_id}/parameters", response_model=list[TestParameterOut])
def list_params(test_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_parameters(conn, test_id)


@router.post("/orders", response_model=TestOrderOut, status_code=201)
def create_order(p: TestOrderCreate, conn: Connection = Depends(get_db_connection)):
    data = p.model_dump(exclude={"test_ids"})
    oid = q.create_order(conn, data)
    for tid in p.test_ids:
        q.add_order_item(conn, oid, tid)
    row = q.get_order(conn, oid)
    return {**row, "test_ids": p.test_ids}


@router.get("/orders/{order_id}/items", response_model=list[TestOrderItemOut])
def order_items(order_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_order_items(conn, order_id)


@router.post("/results", response_model=TestResultOut, status_code=201)
def create_result(p: TestResultCreate, conn: Connection = Depends(get_db_connection)):
    data = p.model_dump(exclude={"items"})
    rid = q.create_result(conn, data)
    for item in p.items:
        q.add_result_item(conn, {**item.model_dump(), "result_id": rid})
    return {**q.get_result(conn, rid), "items": q.list_result_items(conn, rid)}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import hospital_queries as q
from schemas.hospital import (
    HospitalCreate, HospitalOut, DepartmentCreate, DepartmentOut,
    DoctorHospitalCreate, DoctorAtHospital,
)

router = APIRouter(prefix="/hospitals", tags=["hospital"])


@router.post("", response_model=HospitalOut, status_code=201)
def create(p: HospitalCreate, conn: Connection = Depends(get_db_connection)):
    hid = q.create_hospital(conn, p.model_dump())
    return q.get_hospital(conn, hid)


@router.get("", response_model=list[HospitalOut])
def list_all(limit: int = 100, offset: int = 0,
             conn: Connection = Depends(get_db_connection)):
    return q.list_hospitals(conn, limit, offset)


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_one(hospital_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_hospital(conn, hospital_id)
    if not row:
        raise HTTPException(404, "Hospital not found")
    return row


@router.post("/{hospital_id}/departments", response_model=DepartmentOut, status_code=201)
def create_dept(hospital_id: int, p: DepartmentCreate,
                conn: Connection = Depends(get_db_connection)):
    d = {**p.model_dump(), "hospital_id": hospital_id}
    did = q.create_department(conn, d)
    return {**d, "department_id": did}


@router.get("/{hospital_id}/departments", response_model=list[DepartmentOut])
def list_depts(hospital_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_departments(conn, hospital_id)


@router.post("/{hospital_id}/doctors/{doctor_id}", status_code=201)
def link_doctor(hospital_id: int, doctor_id: int, p: DoctorHospitalCreate,
                conn: Connection = Depends(get_db_connection)):
    q.link_doctor_hospital(conn, {
        **p.model_dump(), "doctor_id": doctor_id, "hospital_id": hospital_id,
    })
    return {"ok": True}


@router.get("/{hospital_id}/doctors", response_model=list[DoctorAtHospital])
def doctors(hospital_id: int, conn: Connection = Depends(get_db_connection)):
    return q.doctors_in_hospital(conn, hospital_id)


@router.put("/{hospital_id}", response_model=HospitalOut)
def update_hosp(hospital_id: int, p: HospitalCreate, 
                conn: Connection = Depends(get_db_connection)):
    if q.update_hospital(conn, hospital_id, p.model_dump()) == 0:
        raise HTTPException(404, "Hospital not found")
    return q.get_hospital(conn, hospital_id)


@router.delete("/{hospital_id}", status_code=204)
def delete_hosp(hospital_id: int, conn: Connection = Depends(get_db_connection)):
    if q.delete_hospital(conn, hospital_id) == 0:
        raise HTTPException(404, "Hospital not found")
    
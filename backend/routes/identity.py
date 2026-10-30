from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import identity_queries as q
from schemas.identity import (
    PersonCreate, PersonOut, UserAccountCreate, UserAccountOut,
    RoleCreate, RoleOut, PatientProfileCreate, PatientProfileOut,
    DoctorProfileCreate, DoctorProfileOut, NurseProfileCreate, NurseProfileOut,
)

router = APIRouter(prefix="/identity", tags=["identity"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----- persons -----
@router.post("/persons", response_model=PersonOut, status_code=201)
def create_person(p: PersonCreate, conn: Connection = Depends(get_db_connection)):
    pid = q.create_person(conn, p.model_dump())
    return q.get_person(conn, pid)


@router.get("/persons", response_model=list[PersonOut])
def list_persons(limit: int = 100, offset: int = 0,
                 conn: Connection = Depends(get_db_connection)):
    return q.list_persons(conn, limit, offset)


@router.get("/persons/{person_id}", response_model=PersonOut)
def get_person(person_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_person(conn, person_id)
    if not row:
        raise HTTPException(404, "Person not found")
    return row


@router.put("/persons/{person_id}", response_model=PersonOut)
def update_person(person_id: int, p: PersonCreate,
                  conn: Connection = Depends(get_db_connection)):
    if q.update_person(conn, person_id, p.model_dump()) == 0:
        raise HTTPException(404, "Person not found")
    return q.get_person(conn, person_id)


@router.delete("/persons/{person_id}", status_code=204)
def delete_person(person_id: int, conn: Connection = Depends(get_db_connection)):
    if q.delete_person(conn, person_id) == 0:
        raise HTTPException(404, "Person not found")


# ----- users -----
@router.post("/users", response_model=UserAccountOut, status_code=201)
def create_user(p: UserAccountCreate, conn: Connection = Depends(get_db_connection)):
    d = p.model_dump()
    d["password_hash"] = pwd.hash(d.pop("password"))
    uid = q.create_user(conn, d)
    return q.get_user(conn, uid)


@router.get("/users/{user_id}", response_model=UserAccountOut)
def get_user(user_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_user(conn, user_id)
    if not row:
        raise HTTPException(404, "User not found")
    return row


# ----- roles -----
@router.post("/roles", response_model=RoleOut, status_code=201)
def create_role(p: RoleCreate, conn: Connection = Depends(get_db_connection)):
    rid = q.create_role(conn, p.role_name)
    return {"role_id": rid, "role_name": p.role_name}


@router.get("/roles", response_model=list[RoleOut])
def list_roles(conn: Connection = Depends(get_db_connection)):
    return q.list_roles(conn)


# ----- profiles -----
@router.post("/patients", response_model=PatientProfileOut, status_code=201)
def create_patient(p: PatientProfileCreate,
                   conn: Connection = Depends(get_db_connection)):
    pid = q.create_patient(conn, p.model_dump())
    return q.get_patient(conn, pid)


@router.get("/patients/{patient_id}", response_model=PatientProfileOut)
def get_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_patient(conn, patient_id)
    if not row:
        raise HTTPException(404, "Patient not found")
    return row


@router.post("/doctors", response_model=DoctorProfileOut, status_code=201)
def create_doctor(p: DoctorProfileCreate,
                  conn: Connection = Depends(get_db_connection)):
    did = q.create_doctor(conn, p.model_dump())
    return q.get_doctor(conn, did)


@router.get("/doctors/{doctor_id}", response_model=DoctorProfileOut)
def get_doctor(doctor_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_doctor(conn, doctor_id)
    if not row:
        raise HTTPException(404, "Doctor not found")
    return row


@router.post("/nurses", response_model=NurseProfileOut, status_code=201)
def create_nurse(p: NurseProfileCreate,
                 conn: Connection = Depends(get_db_connection)):
    nid = q.create_nurse(conn, p.model_dump())
    return q.get_nurse(conn, nid)
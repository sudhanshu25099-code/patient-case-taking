from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import identity_queries as q
from .auth import verify_user 
from schemas.identity import (
    PersonCreate, PersonOut, UserAccountCreate, UserAccountOut,
    RoleCreate, RoleOut, PatientProfileCreate, PatientProfileOut,
    DoctorProfileCreate, DoctorProfileOut, NurseProfileCreate, NurseProfileOut,
    PasswordUpdate, RoleAssignment
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
@router.get("/users")
def list_users(conn: Connection = Depends(get_db_connection)):
    return [dict(u) for u in q.list_users(conn)]


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
@router.get("/patients")
def list_patients(conn: Connection = Depends(get_db_connection)):
    return [dict(p) for p in q.list_patients(conn)]


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


@router.get("/doctors")
def list_doctors(conn: Connection = Depends(get_db_connection)):
    return [dict(d) for d in q.list_doctors(conn)]


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


@router.get("/nurses")
def list_nurses(conn: Connection = Depends(get_db_connection)):
    return [dict(n) for n in q.list_nurses(conn)]


@router.post("/nurses", response_model=NurseProfileOut, status_code=201)
def create_nurse(p: NurseProfileCreate,
                 conn: Connection = Depends(get_db_connection)):
    nid = q.create_nurse(conn, p.model_dump())
    return q.get_nurse(conn, nid)


@router.get("/nurses/{nurse_id}")
def get_nurse(nurse_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_nurse(conn, nurse_id)
    if not row:
        raise HTTPException(404, "Nurse not found")
    return dict(row)


@router.patch("/users/{user_id}/password")
def change_password(
    user_id: int, 
    p: PasswordUpdate, 
    conn: Connection = Depends(get_db_connection),
    current_user: dict = Depends(verify_user)
):
    new_hash = pwd.hash(p.new_password)
    if q.update_password(conn, user_id, new_hash) == 0:
        raise HTTPException(404, "User not found")
    return {"ok": True, "message": "Password updated successfully"}


@router.post("/users/{user_id}/roles", status_code=201)
def assign_role(
    user_id: int, 
    p: RoleAssignment, 
    conn: Connection = Depends(get_db_connection),
    current_user: dict = Depends(verify_user)
):
    q.assign_role(conn, user_id, p.role_id)
    return {"ok": True, "message": "Role assigned"}

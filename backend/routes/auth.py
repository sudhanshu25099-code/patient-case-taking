from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import auth_queries as q  

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBasic()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(
    credentials: HTTPBasicCredentials = Depends(security), 
    conn: Connection = Depends(get_db_connection)
) -> dict:
    """Dependency to protect routes. Returns the user dict if valid."""
    user = q.get_user_by_username(conn, credentials.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    try:
        is_valid = pwd.verify(credentials.password, user["password_hash"])
    except Exception:
        is_valid = False
        
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
        
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

@router.get("/me")
def get_me(
    current_user: dict = Depends(verify_user),
    conn: Connection = Depends(get_db_connection)
):
    """
    Returns rich authenticated user context:
    - User account details
    - Roles & primary role (Admin, Doctor, Nurse, Patient)
    - Associated profile records (doctor_profile, nurse_profile, patient_profile)
    """
    uid = current_user["user_id"]
    pid = current_user["person_id"]
    
    person = conn.execute(
        text("SELECT full_name, email, phone, gender, date_of_birth FROM person WHERE person_id = :p"),
        {"p": pid}
    ).mappings().first()
    
    roles = [
        r[0] for r in conn.execute(
            text("SELECT r.role_name FROM role r JOIN user_role ur ON ur.role_id = r.role_id WHERE ur.user_id = :u"),
            {"u": uid}
        ).fetchall()
    ]
    
    doctor = conn.execute(
        text("SELECT doctor_id, specialization, license_no, experience_years, consultation_fee FROM doctor_profile WHERE person_id = :p"),
        {"p": pid}
    ).mappings().first()
    
    nurse = conn.execute(
        text("SELECT nurse_id, department_id, employee_no, shift FROM nurse_profile WHERE person_id = :p"),
        {"p": pid}
    ).mappings().first()
    
    patient = conn.execute(
        text("SELECT patient_id, blood_group, emergency_contact_name, emergency_contact_phone, abha_linked FROM patient_profile WHERE person_id = :p"),
        {"p": pid}
    ).mappings().first()
    
    primary_role = "Patient"
    if any(r in ["Super Admin", "Hospital Admin"] for r in roles):
        primary_role = "Admin"
    elif "Doctor" in roles:
        primary_role = "Doctor"
    elif "Nurse" in roles:
        primary_role = "Nurse"
    elif "Patient" in roles:
        primary_role = "Patient"

    return {
        "user_id": uid,
        "username": current_user["username"],
        "person_id": pid,
        "full_name": person["full_name"] if person else current_user["username"],
        "email": person["email"] if (person and person["email"]) else current_user["email"],
        "phone": person["phone"] if person else None,
        "gender": person["gender"] if person else None,
        "date_of_birth": str(person["date_of_birth"]) if (person and person["date_of_birth"]) else None,
        "roles": roles,
        "primary_role": primary_role,
        "doctor": dict(doctor) if doctor else None,
        "nurse": dict(nurse) if nurse else None,
        "patient": dict(patient) if patient else None,
    }

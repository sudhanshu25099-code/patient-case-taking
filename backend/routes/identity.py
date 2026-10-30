from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.cursor import MySQLCursor
from database import get_db
from schemas.identity import PersonCreate, PersonResponse, PatientProfileCreate, DoctorProfileCreate

router = APIRouter()

@router.post("/person", response_model=PersonResponse, status_code=201)
def create_person(person: PersonCreate, cursor: MySQLCursor = Depends(get_db)):
    query = """
        INSERT INTO PERSON (full_name, date_of_birth, gender, phone, address)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (person.full_name, person.date_of_birth, person.gender, person.phone, person.address)
    cursor.execute(query, values)
    person_id = cursor.lastrowid
    
    return PersonResponse(person_id=person_id, **person.dict())

@router.post("/patient", status_code=201)
def create_patient_profile(patient: PatientProfileCreate, cursor: MySQLCursor = Depends(get_db)):
    query = """
        INSERT INTO PATIENT_PROFILE (person_id, blood_group, emergency_contact, allergies)
        VALUES (%s, %s, %s, %s)
    """
    values = (patient.person_id, patient.blood_group, patient.emergency_contact, patient.allergies)
    cursor.execute(query, values)
    return {"message": "Patient profile created successfully", "patient_id": patient.person_id}

@router.post("/doctor", status_code=201)
def create_doctor_profile(doctor: DoctorProfileCreate, cursor: MySQLCursor = Depends(get_db)):
    query = """
        INSERT INTO DOCTOR_PROFILE (person_id, specialization, qualification, consultation_fee)
        VALUES (%s, %s, %s, %s)
    """
    values = (doctor.person_id, doctor.specialization, doctor.qualification, doctor.consultation_fee)
    cursor.execute(query, values)
    return {"message": "Doctor profile created successfully", "doctor_id": doctor.person_id}
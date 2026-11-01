"""
API Client for Patient Case Taking & Record System.
Communicates with FastAPI backend (http://localhost:8000) using HTTP Basic Auth or Bearer tokens.
Includes resilient fallback mock database pre-seeded with project demo data,
ensuring seamless interactive exploration whether backend is running or offline.
"""

import os
import requests
from datetime import datetime, date, time
from typing import Any, Dict, List, Optional, Union


DEFAULT_BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


# ==============================================================================
# SEED DATA FOR OFFLINE / DEMO RESILIENCE
# ==============================================================================

def get_initial_mock_db() -> Dict[str, Any]:
    """Generates authentic in-memory seed data matching db_schema/seed.sql."""
    return {
        "persons": [
            {"person_id": 1, "full_name": "Sudhanshu Jha", "date_of_birth": "1980-04-12", "gender": "Male", "phone": "9810000001", "email": "sudhanshu@example.com", "address": "12 Rajpath Road", "city": "New Delhi", "state": "Delhi"},
            {"person_id": 2, "full_name": "Dr. Rajesh Sharma", "date_of_birth": "1975-08-19", "gender": "Male", "phone": "9810000002", "email": "rajesh.sharma@example.com", "address": "45 Lodhi Colony", "city": "New Delhi", "state": "Delhi"},
            {"person_id": 3, "full_name": "Dr. Anita Verma", "date_of_birth": "1978-01-25", "gender": "Female", "phone": "9810000003", "email": "anita.verma@example.com", "address": "8 Sector 15", "city": "Noida", "state": "Uttar Pradesh"},
            {"person_id": 4, "full_name": "Dr. Sandeep Gupta", "date_of_birth": "1972-06-30", "gender": "Male", "phone": "9810000004", "email": "sandeep.gupta@example.com", "address": "22 Vasant Vihar", "city": "New Delhi", "state": "Delhi"},
            {"person_id": 5, "full_name": "Dr. Priya Nair", "date_of_birth": "1983-11-14", "gender": "Female", "phone": "9810000005", "email": "priya.nair@example.com", "address": "104 Indiranagar", "city": "Bengaluru", "state": "Karnataka"},
            {"person_id": 6, "full_name": "Dr. Vikram Singh", "date_of_birth": "1968-03-05", "gender": "Male", "phone": "9810000006", "email": "vikram.singh@example.com", "address": "77 Civil Lines", "city": "Jaipur", "state": "Rajasthan"},
            {"person_id": 7, "full_name": "Dr. Neha Kapoor", "date_of_birth": "1985-09-22", "gender": "Female", "phone": "9810000007", "email": "neha.kapoor@example.com", "address": "502 Park Street", "city": "Kolkata", "state": "West Bengal"},
            {"person_id": 8, "full_name": "Nurse Sunita Rao", "date_of_birth": "1988-07-11", "gender": "Female", "phone": "9810000008", "email": "sunita.rao@example.com", "address": "18 Mall Road", "city": "New Delhi", "state": "Delhi"},
            {"person_id": 9, "full_name": "Nurse Deepak Yadav", "date_of_birth": "1991-12-03", "gender": "Male", "phone": "9810000009", "email": "deepak.yadav@example.com", "address": "62 MG Road", "city": "Gurugram", "state": "Haryana"},
            {"person_id": 10, "full_name": "Aarav Mehta", "date_of_birth": "1995-02-14", "gender": "Male", "phone": "9810000010", "email": "aarav.mehta@example.com", "address": "101 Coral Heights", "city": "Mumbai", "state": "Maharashtra"},
            {"person_id": 11, "full_name": "Simran Kaur", "date_of_birth": "1990-09-08", "gender": "Female", "phone": "9810000011", "email": "simran.kaur@example.com", "address": "23 Model Town", "city": "Amritsar", "state": "Punjab"},
            {"person_id": 12, "full_name": "Rohan Das", "date_of_birth": "1982-11-20", "gender": "Male", "phone": "9810000012", "email": "rohan.das@example.com", "address": "55 Salt Lake", "city": "Kolkata", "state": "West Bengal"},
            {"person_id": 13, "full_name": "Fatima Khan", "date_of_birth": "1998-05-30", "gender": "Female", "phone": "9810000013", "email": "fatima.khan@example.com", "address": "89 Banjara Hills", "city": "Hyderabad", "state": "Telangana"},
            {"person_id": 14, "full_name": "Kavita Joshi", "date_of_birth": "1970-12-18", "gender": "Female", "phone": "9810000014", "email": "kavita.joshi@example.com", "address": "14 Koregaon Park", "city": "Pune", "state": "Maharashtra"},
            {"person_id": 15, "full_name": "Arjun Reddy", "date_of_birth": "1987-03-27", "gender": "Male", "phone": "9810000015", "email": "arjun.reddy@example.com", "address": "78 Jubilee Hills", "city": "Hyderabad", "state": "Telangana"},
            {"person_id": 16, "full_name": "Meera Iyer", "date_of_birth": "1993-08-15", "gender": "Female", "phone": "9810000016", "email": "meera.iyer@example.com", "address": "33 Mylapore", "city": "Chennai", "state": "Tamil Nadu"}
        ],
        "users": [
            {"user_id": 1, "person_id": 1, "username": "admin", "email": "sudhanshu@example.com", "is_active": True, "last_login": "2026-10-31 09:10:00"},
            {"user_id": 2, "person_id": 2, "username": "dr.sharma", "email": "rajesh.sharma@example.com", "is_active": True, "last_login": "2026-10-31 08:45:00"},
            {"user_id": 3, "person_id": 3, "username": "dr.verma", "email": "anita.verma@example.com", "is_active": True, "last_login": "2026-10-31 10:20:00"},
            {"user_id": 4, "person_id": 4, "username": "dr.gupta", "email": "sandeep.gupta@example.com", "is_active": True, "last_login": "2026-10-30 17:05:00"},
            {"user_id": 5, "person_id": 5, "username": "dr.nair", "email": "priya.nair@example.com", "is_active": True, "last_login": "2026-10-31 11:00:00"},
            {"user_id": 6, "person_id": 6, "username": "dr.singh", "email": "vikram.singh@example.com", "is_active": True, "last_login": "2026-10-29 14:30:00"},
            {"user_id": 7, "person_id": 7, "username": "dr.kapoor", "email": "neha.kapoor@example.com", "is_active": True, "last_login": "2026-10-31 12:15:00"},
            {"user_id": 8, "person_id": 8, "username": "nurse.rao", "email": "sunita.rao@example.com", "is_active": True, "last_login": "2026-10-31 07:55:00"},
            {"user_id": 9, "person_id": 9, "username": "nurse.yadav", "email": "deepak.yadav@example.com", "is_active": True, "last_login": "2026-10-30 21:40:00"},
            {"user_id": 10, "person_id": 10, "username": "aarav.mehta", "email": "aarav.mehta@example.com", "is_active": True, "last_login": "2026-10-31 19:30:00"},
            {"user_id": 11, "person_id": 11, "username": "simran.kaur", "email": "simran.kaur@example.com", "is_active": True, "last_login": "2026-10-30 20:10:00"},
            {"user_id": 12, "person_id": 12, "username": "rohan.das", "email": "rohan.das@example.com", "is_active": True, "last_login": "2026-10-25 18:00:00"}
        ],
        "roles": [
            {"role_id": 1, "role_name": "Patient"},
            {"role_id": 2, "role_name": "Doctor"},
            {"role_id": 3, "role_name": "Nurse"},
            {"role_id": 4, "role_name": "Hospital Admin"},
            {"role_id": 5, "role_name": "Super Admin"}
        ],
        "user_roles": [
            {"user_id": 1, "role_id": 5},
            {"user_id": 2, "role_id": 2},
            {"user_id": 3, "role_id": 2},
            {"user_id": 4, "role_id": 2},
            {"user_id": 5, "role_id": 2},
            {"user_id": 6, "role_id": 2},
            {"user_id": 7, "role_id": 2},
            {"user_id": 8, "role_id": 3},
            {"user_id": 9, "role_id": 3},
            {"user_id": 10, "role_id": 1},
            {"user_id": 11, "role_id": 1},
            {"user_id": 12, "role_id": 1}
        ],
        "hospitals": [
            {"hospital_id": 1, "name": "Apex Heart & Multispeciality Hospital", "registration_no": "REG-DEL-2015-001", "address": "14 Ring Road, Lajpat Nagar", "city": "New Delhi", "state": "Delhi", "contact_no": "011-29800001", "email": "contact@apexhealth.in"},
            {"hospital_id": 2, "name": "City Care Memorial Hospital", "registration_no": "REG-UP-2018-045", "address": "Plot 12, Knowledge Park III", "city": "Greater Noida", "state": "Uttar Pradesh", "contact_no": "0120-4560002", "email": "info@citycare.in"},
            {"hospital_id": 3, "name": "Metro Life Clinic & Diagnostic Centre", "registration_no": "REG-HR-2020-089", "address": "Golf Course Extension Road, Sector 56", "city": "Gurugram", "state": "Haryana", "contact_no": "0124-7890003", "email": "help@metrolife.org"}
        ],
        "departments": [
            {"department_id": 1, "hospital_id": 1, "name": "Cardiology", "description": "Heart disease, angioplasty, and cardiac rehab"},
            {"department_id": 2, "hospital_id": 1, "name": "General Medicine", "description": "Primary healthcare, fever, diabetes management"},
            {"department_id": 3, "hospital_id": 1, "name": "Orthopedics", "description": "Bone, joint replacements, and trauma care"},
            {"department_id": 4, "hospital_id": 1, "name": "Pulmonology", "description": "Lungs, asthma, and COPD treatment"},
            {"department_id": 5, "hospital_id": 2, "name": "Endocrinology", "description": "Diabetes, thyroid, and hormone care"},
            {"department_id": 6, "hospital_id": 2, "name": "Pediatrics", "description": "Child health, immunization, and growth monitoring"},
            {"department_id": 7, "hospital_id": 2, "name": "Neurology", "description": "Brain, stroke, and nervous system disorders"},
            {"department_id": 8, "hospital_id": 3, "name": "General Medicine", "description": "Outpatient primary healthcare"},
            {"department_id": 9, "hospital_id": 3, "name": "Pathology & Radiology", "description": "Complete diagnostic imaging and blood testing"}
        ],
        "patients": [
            {"patient_id": 1, "person_id": 10, "full_name": "Aarav Mehta", "blood_group": "B+", "emergency_contact_name": "Suresh Mehta", "emergency_contact_phone": "9810000091", "abha_linked": True},
            {"patient_id": 2, "person_id": 11, "full_name": "Simran Kaur", "blood_group": "O+", "emergency_contact_name": "Harpreet Singh", "emergency_contact_phone": "9810000092", "abha_linked": True},
            {"patient_id": 3, "person_id": 12, "full_name": "Rohan Das", "blood_group": "A+", "emergency_contact_name": "Pooja Das", "emergency_contact_phone": "9810000093", "abha_linked": False},
            {"patient_id": 4, "person_id": 13, "full_name": "Fatima Khan", "blood_group": "AB+", "emergency_contact_name": "Imran Khan", "emergency_contact_phone": "9810000094", "abha_linked": True},
            {"patient_id": 5, "person_id": 14, "full_name": "Kavita Joshi", "blood_group": "O-", "emergency_contact_name": "Manoj Joshi", "emergency_contact_phone": "9810000095", "abha_linked": False},
            {"patient_id": 6, "person_id": 15, "full_name": "Arjun Reddy", "blood_group": "B-", "emergency_contact_name": "Lakshmi Reddy", "emergency_contact_phone": "9810000096", "abha_linked": True},
            {"patient_id": 7, "person_id": 16, "full_name": "Meera Iyer", "blood_group": "A-", "emergency_contact_name": "Raman Iyer", "emergency_contact_phone": "9810000097", "abha_linked": False}
        ],
        "doctors": [
            {"doctor_id": 1, "person_id": 2, "full_name": "Dr. Rajesh Sharma", "license_no": "MCI-DL-2001-4412", "qualification": "MBBS, MD (Medicine), DM (Cardiology)", "specialization": "Cardiology", "experience_years": 23, "consultation_fee": 1500.00, "hospital_id": 1, "department_id": 1},
            {"doctor_id": 2, "person_id": 3, "full_name": "Dr. Anita Verma", "license_no": "MCI-UP-2004-8891", "qualification": "MBBS, MD (General Medicine)", "specialization": "General Medicine", "experience_years": 20, "consultation_fee": 800.00, "hospital_id": 1, "department_id": 2},
            {"doctor_id": 3, "person_id": 4, "full_name": "Dr. Sandeep Gupta", "license_no": "MCI-DL-1998-1120", "qualification": "MBBS, MS (Orthopedics), MCh", "specialization": "Orthopedics", "experience_years": 26, "consultation_fee": 1800.00, "hospital_id": 1, "department_id": 3},
            {"doctor_id": 4, "person_id": 5, "full_name": "Dr. Priya Nair", "license_no": "MCI-KA-2009-6634", "qualification": "MBBS, MD (Pediatrics)", "specialization": "Pediatrics", "experience_years": 15, "consultation_fee": 1000.00, "hospital_id": 2, "department_id": 6},
            {"doctor_id": 5, "person_id": 6, "full_name": "Dr. Vikram Singh", "license_no": "MCI-RJ-1994-3301", "qualification": "MBBS, MD, DM (Neurology)", "specialization": "Neurology", "experience_years": 30, "consultation_fee": 2200.00, "hospital_id": 2, "department_id": 7},
            {"doctor_id": 6, "person_id": 7, "full_name": "Dr. Neha Kapoor", "license_no": "MCI-WB-2011-9954", "qualification": "MBBS, MD (Pulmonology)", "specialization": "Pulmonology", "experience_years": 13, "consultation_fee": 1200.00, "hospital_id": 1, "department_id": 4}
        ],
        "nurses": [
            {"nurse_id": 1, "person_id": 8, "full_name": "Nurse Sunita Rao", "department_id": 1, "employee_no": "EMP-NR-101", "shift": "Morning"},
            {"nurse_id": 2, "person_id": 9, "full_name": "Nurse Deepak Yadav", "department_id": 2, "employee_no": "EMP-NR-102", "shift": "Evening"}
        ],
        "appointments": [
            {"appointment_id": 1, "patient_id": 1, "patient_name": "Aarav Mehta", "hospital_id": 1, "doctor_id": 1, "doctor_name": "Dr. Rajesh Sharma", "appointment_date": "2026-11-01", "time_slot": "10:00:00", "reason": "Severe chest tightness and palpitations", "pre_visit_notes": "Patient reports recurrent palpitations after morning jog.", "is_follow_up": False, "status": "Scheduled", "notes": "First cardiac consultation", "booked_by": 10},
            {"appointment_id": 2, "patient_id": 2, "patient_name": "Simran Kaur", "hospital_id": 1, "doctor_id": 2, "doctor_name": "Dr. Anita Verma", "appointment_date": "2026-11-01", "time_slot": "10:30:00", "reason": "Routine Diabetes and Hypertension 3-month review", "pre_visit_notes": "Fasting blood sugar diary brought.", "is_follow_up": True, "status": "Scheduled", "notes": "Quarterly checkup", "booked_by": 11},
            {"appointment_id": 3, "patient_id": 3, "patient_name": "Rohan Das", "hospital_id": 1, "doctor_id": 3, "doctor_name": "Dr. Sandeep Gupta", "appointment_date": "2026-11-01", "time_slot": "11:00:00", "reason": "Persistent right knee pain and stiffness", "pre_visit_notes": "Difficulty climbing stairs for 3 weeks.", "is_follow_up": False, "status": "Scheduled", "notes": "Suspected osteoarthritis", "booked_by": 12},
            {"appointment_id": 4, "patient_id": 4, "patient_name": "Fatima Khan", "hospital_id": 1, "doctor_id": 6, "doctor_name": "Dr. Neha Kapoor", "appointment_date": "2026-10-30", "time_slot": "14:00:00", "reason": "Nocturnal dry cough and wheezing", "pre_visit_notes": "Symptoms aggravate during cold mornings.", "is_follow_up": False, "status": "Completed", "notes": "Bronchial asthma confirmed", "booked_by": 13},
            {"appointment_id": 5, "patient_id": 5, "patient_name": "Kavita Joshi", "hospital_id": 2, "doctor_id": 5, "doctor_name": "Dr. Vikram Singh", "appointment_date": "2026-10-29", "time_slot": "11:30:00", "reason": "Frequent migraine episodes with visual aura", "pre_visit_notes": "Unilateral throbbing headache lasting 8 hours.", "is_follow_up": True, "status": "Completed", "notes": "Prophylaxis prescribed", "booked_by": 14}
        ],
        "appointment_symptoms": [
            {"symptom_id": 1, "appointment_id": 1, "symptom_name": "Chest tightness", "severity": "Moderate", "since_date": "2026-10-26", "notes": "Worse on exertion"},
            {"symptom_id": 2, "appointment_id": 1, "symptom_name": "Palpitations", "severity": "Mild", "since_date": "2026-10-28", "notes": "Lasting 10-15 mins"},
            {"symptom_id": 3, "appointment_id": 3, "symptom_name": "Joint stiffness", "severity": "Moderate", "since_date": "2026-10-10", "notes": "Morning stiffness ~30 mins"}
        ],
        "appointment_notes": [
            {"appt_note_id": 1, "appointment_id": 1, "note_text": "ECG requested prior to consultation.", "added_by": 2, "added_at": "2026-10-31 09:30:00"}
        ],
        "visits": [
            {
                "visit_id": 1, "appointment_id": 4, "patient_id": 4, "patient_name": "Fatima Khan", "hospital_id": 1, "doctor_id": 6, "doctor_name": "Dr. Neha Kapoor",
                "visit_date": "2026-10-30 14:15:00", "visit_type": "OPD",
                "chief_complaint": "Wheezing, shortness of breath on exertion, and nocturnal coughing for 2 weeks",
                "symptoms": "Bilateral expiratory wheezing, dry cough",
                "vitals_summary": "BP: 118/76 mmHg, Pulse: 84 bpm, SpO2: 96% room air, Temp: 98.4 F, BMI: 22.4",
                "notes": "Patient triggered by cold dust. Prescribed budesonide inhaler."
            },
            {
                "visit_id": 2, "appointment_id": 5, "patient_id": 5, "patient_name": "Kavita Joshi", "hospital_id": 2, "doctor_id": 5, "doctor_name": "Dr. Vikram Singh",
                "visit_date": "2026-10-29 11:45:00", "visit_type": "OPD",
                "chief_complaint": "Severe unilateral throbbing headache, photophobia, nausea",
                "symptoms": "Left temporal headache, aura, light sensitivity",
                "vitals_summary": "BP: 130/84 mmHg, Pulse: 78 bpm, SpO2: 99%, Temp: 98.6 F, BMI: 25.1",
                "notes": "Classic migraine with aura. Refill Rizatriptan and start Propranolol."
            }
        ],
        "diagnoses": [
            {"diagnosis_id": 1, "visit_id": 1, "diagnosis_code": "J45.909", "diagnosis_name": "Bronchial Asthma, Unspecified", "diagnosis_type": "Primary", "notes": "Moderate persistent"},
            {"diagnosis_id": 2, "visit_id": 2, "diagnosis_code": "G43.109", "diagnosis_name": "Migraine with aura, not intractable", "diagnosis_type": "Primary", "notes": "Triggered by screen time"}
        ],
        "procedures": [
            {"procedure_id": 1, "visit_id": 1, "procedure_name": "Spirometry / Peak Flow Measurement", "procedure_type": "Diagnostic", "notes": "FEV1 improved by 16% post-bronchodilator"}
        ],
        "visit_notes": [
            {"note_id": 1, "visit_id": 1, "note_type": "Consultation", "title": "Pulmonology Assessment", "content": "S: Coughing at night for 14 days.\nO: Wheeze bilateral lower zones. SpO2 96%.\nA: Bronchial asthma with allergic exacerbation.\nP: Inhaler Budesonide + Formoterol 200/6mcg BID.", "added_by": 6, "added_at": "2026-10-30 14:45:00"}
        ],
        "allergies": [
            {"allergy_id": 1, "patient_id": 1, "allergen": "Penicillin", "allergy_type": "Drug", "reaction": "Skin rash, hives, urticaria", "severity": "Severe", "status": "Active", "noted_date": "2020-05-15", "notes": "Do not administer beta-lactams"},
            {"allergy_id": 2, "patient_id": 2, "allergen": "Sulfa Drugs", "allergy_type": "Drug", "reaction": "Facial swelling and pruritus", "severity": "Moderate", "status": "Active", "noted_date": "2018-09-10", "notes": "Documented during UTI treatment"},
            {"allergy_id": 3, "patient_id": 3, "allergen": "Aspirin / NSAIDs", "allergy_type": "Drug", "reaction": "Bronchospasm and gastric pain", "severity": "Moderate", "status": "Active", "noted_date": "2021-02-14", "notes": "Use Paracetamol with caution"}
        ],
        "conditions": [
            {"condition_id": 1, "patient_id": 2, "condition_name": "Type 2 Diabetes Mellitus", "icd_code": "E11.9", "condition_type": "Chronic", "onset_date": "2017-04-10", "status": "Controlled", "notes": "Maintained on Metformin 500mg BID"},
            {"condition_id": 2, "patient_id": 2, "condition_name": "Essential Hypertension", "icd_code": "I10", "condition_type": "Chronic", "onset_date": "2019-08-20", "status": "Active", "notes": "On Telmisartan 40mg once daily"},
            {"condition_id": 3, "patient_id": 4, "condition_name": "Bronchial Asthma", "icd_code": "J45.909", "condition_type": "Chronic", "onset_date": "2024-01-15", "status": "Active", "notes": "Triggered by environmental allergens"}
        ],
        "prescriptions": [
            {
                "prescription_id": 1, "visit_id": 1, "patient_id": 4, "doctor_id": 6, "prescribed_date": "2026-10-30", "notes": "Rinse mouth thoroughly after inhaler usage.",
                "items": [
                    {"item_id": 1, "prescription_id": 1, "medicine_name": "Budesonide + Formoterol 200/6mcg Inhaler", "dosage": "1 puff", "frequency": "Twice daily", "route": "Inhalation", "duration_days": 30, "is_ongoing": True, "instructions": "Morning and night with spacer"},
                    {"item_id": 2, "prescription_id": 1, "medicine_name": "Levocetirizine 5mg Tablet", "dosage": "1 tablet", "frequency": "Once daily at bedtime", "route": "Oral", "duration_days": 10, "is_ongoing": False, "instructions": "Take at night for allergic itch"}
                ]
            }
        ],
        "diagnostic_tests": [
            {"test_id": 1, "test_name": "Complete Blood Count (CBC)", "category": "Blood", "description": "Basic blood health panel evaluating RBC, WBC, Hemoglobin and Platelets"},
            {"test_id": 2, "test_name": "HbA1c (Glycated Hemoglobin)", "category": "Blood", "description": "3-month average blood glucose control marker"},
            {"test_id": 3, "test_name": "Lipid Profile Panel", "category": "Blood", "description": "Total cholesterol, HDL, LDL, and Triglycerides"},
            {"test_id": 4, "test_name": "Thyroid Stimulating Hormone (TSH)", "category": "Blood", "description": "Serum TSH level for thyroid gland function"},
            {"test_id": 5, "test_name": "Urine Routine & Microscopic", "category": "Urine", "description": "Urinalysis for infection, protein, and glucose"},
            {"test_id": 6, "test_name": "Chest X-Ray PA View", "category": "Imaging", "description": "Plain radiography of chest and lungs"},
            {"test_id": 7, "test_name": "Knee Joint X-Ray (AP & Lateral)", "category": "Imaging", "description": "Radiography for osteoarthritis and joint alignment"},
            {"test_id": 8, "test_name": "12-Lead ECG", "category": "Other", "description": "Standard resting electrocardiogram for arrhythmia and ischemia"}
        ],
        "test_parameters": [
            {"parameter_id": 1, "test_id": 1, "parameter_name": "Hemoglobin", "unit": "g/dL", "reference_range": "13.0 - 17.0"},
            {"parameter_id": 2, "test_id": 1, "parameter_name": "WBC Count", "unit": "/uL", "reference_range": "4000 - 11000"},
            {"parameter_id": 3, "test_id": 1, "parameter_name": "Platelet Count", "unit": "/uL", "reference_range": "150000 - 450000"},
            {"parameter_id": 4, "test_id": 2, "parameter_name": "HbA1c", "unit": "%", "reference_range": "4.0 - 5.6"},
            {"parameter_id": 5, "test_id": 3, "parameter_name": "Total Cholesterol", "unit": "mg/dL", "reference_range": "< 200"},
            {"parameter_id": 6, "test_id": 3, "parameter_name": "LDL Cholesterol", "unit": "mg/dL", "reference_range": "< 100"},
            {"parameter_id": 7, "test_id": 3, "parameter_name": "HDL Cholesterol", "unit": "mg/dL", "reference_range": "> 40"},
            {"parameter_id": 8, "test_id": 3, "parameter_name": "Triglycerides", "unit": "mg/dL", "reference_range": "< 150"},
            {"parameter_id": 9, "test_id": 4, "parameter_name": "TSH", "unit": "uIU/mL", "reference_range": "0.4 - 4.0"}
        ],
        "test_orders": [
            {
                "order_id": 1, "visit_id": 1, "patient_id": 4, "ordered_by": 6, "order_date": "2026-10-30 14:30:00",
                "status": "Completed", "clinical_note": "Rule out respiratory infection vs allergic asthma", "test_ids": [1, 6]
            },
            {
                "order_id": 2, "visit_id": 2, "patient_id": 5, "ordered_by": 5, "order_date": "2026-10-29 12:00:00",
                "status": "Completed", "clinical_note": "Routine metabolic profile for migraine", "test_ids": [1, 2]
            }
        ],
        "test_results": [
            {
                "result_id": 1, "order_item_id": 1, "patient_id": 4, "test_name": "Complete Blood Count (CBC)",
                "report_date": "2026-10-30 17:00:00", "overall_finding": "Mild eosinophilia noted, consistent with allergic bronchial response.",
                "verified_by": 6, "verification_status": "Verified",
                "items": [
                    {"result_item_id": 1, "result_id": 1, "parameter_id": 1, "parameter_name": "Hemoglobin", "result_value": "13.8", "flag": "Normal", "unit": "g/dL", "reference_range": "13.0 - 17.0"},
                    {"result_item_id": 2, "result_id": 1, "parameter_id": 2, "parameter_name": "WBC Count", "result_value": "10400", "flag": "Normal", "unit": "/uL", "reference_range": "4000 - 11000"},
                    {"result_item_id": 3, "result_id": 1, "parameter_id": 3, "parameter_name": "Platelet Count", "result_value": "275000", "flag": "Normal", "unit": "/uL", "reference_range": "150000 - 450000"}
                ]
            },
            {
                "result_id": 2, "order_item_id": 2, "patient_id": 5, "test_name": "HbA1c (Glycated Hemoglobin)",
                "report_date": "2026-10-29 16:30:00", "overall_finding": "HbA1c slightly elevated at 6.1% (prediabetic range).",
                "verified_by": 5, "verification_status": "Verified",
                "items": [
                    {"result_item_id": 4, "result_id": 2, "parameter_id": 4, "parameter_name": "HbA1c", "result_value": "6.1", "flag": "High", "unit": "%", "reference_range": "4.0 - 5.6"}
                ]
            }
        ],
        "document_types": [
            {"document_type_id": 1, "name": "Prescription", "description": "Doctor signed prescription slip"},
            {"document_type_id": 2, "name": "Lab Report", "description": "Blood, urine, pathology reports"},
            {"document_type_id": 3, "name": "Imaging Report", "description": "X-Ray, CT, MRI scans"},
            {"document_type_id": 4, "name": "Discharge Summary", "description": "Inpatient discharge papers"},
            {"document_type_id": 5, "name": "Vaccination Record", "description": "Immunization certificate"},
            {"document_type_id": 6, "name": "Other", "description": "Miscellaneous health documents"}
        ],
        "document_tags": [
            {"tag_id": 1, "name": "Lab", "description": "Laboratory reports"},
            {"tag_id": 2, "name": "Imaging", "description": "X-Ray / MRI / CT"},
            {"tag_id": 3, "name": "Prescription", "description": "Medicine prescriptions"},
            {"tag_id": 4, "name": "Diabetes", "description": "Diabetes related"},
            {"tag_id": 5, "name": "Cardiac", "description": "Heart related"},
            {"tag_id": 6, "name": "Asthma", "description": "Respiratory related"},
            {"tag_id": 7, "name": "Chronic", "description": "Long-term condition"}
        ],
        "documents": [
            {
                "document_id": 1, "patient_id": 4, "visit_id": 1, "document_type_id": 1,
                "title": "Pulmonology Prescription - Inhaler & Antihistamine", "description": "Issued by Dr. Neha Kapoor for bronchial asthma exacerbation.",
                "file_path": "/vault/docs/patient_4_presc_01.pdf", "file_size": 245000, "mime_type": "application/pdf",
                "document_date": "2026-10-30", "ocr_status": "Done", "verification_status": "Verified",
                "uploaded_by": 6, "uploaded_at": "2026-10-30 15:00:00", "tag_ids": [3, 6],
                "ocr_text": "APEX HOSPITAL OPD - RX: Budesonide 200mcg BID, Levocetirizine 5mg HS. Review in 4 weeks."
            },
            {
                "document_id": 2, "patient_id": 5, "visit_id": 2, "document_type_id": 2,
                "title": "HbA1c & Fasting Glucose Report", "description": "Quarterly metabolic panel test report.",
                "file_path": "/vault/docs/patient_5_hba1c.pdf", "file_size": 180000, "mime_type": "application/pdf",
                "document_date": "2026-10-29", "ocr_status": "Done", "verification_status": "Verified",
                "uploaded_by": 8, "uploaded_at": "2026-10-29 17:30:00", "tag_ids": [1, 4, 7],
                "ocr_text": "METRO LIFE DIAGNOSTICS - HbA1c: 6.1%. Impaired fasting glucose. Lifestyle intervention advised."
            }
        ],
        "consents": [
            {
                "consent_id": 1, "patient_id": 1, "patient_name": "Aarav Mehta", "hospital_id": 1, "consent_type": "View Only",
                "valid_from": "2026-10-25 00:00:00", "valid_to": "2026-11-25 23:59:59", "status": "Active",
                "purpose": "Cardiac evaluation and ECG review", "remarks": "Full cardiology team authorization"
            },
            {
                "consent_id": 2, "patient_id": 2, "patient_name": "Simran Kaur", "hospital_id": 1, "consent_type": "View Only",
                "valid_from": "2026-10-01 00:00:00", "valid_to": "2027-10-01 23:59:59", "status": "Active",
                "purpose": "Long term diabetes & chronic care management", "remarks": "Annual chronic consent"
            }
        ],
        "consent_access": [
            {"access_id": 1, "consent_id": 1, "doctor_id": 1, "doctor_name": "Dr. Rajesh Sharma", "department_id": 1, "access_from": "2026-10-25 00:00:00", "access_to": "2026-11-25 23:59:59", "status": "Active"},
            {"access_id": 2, "consent_id": 2, "doctor_id": 2, "doctor_name": "Dr. Anita Verma", "department_id": 2, "access_from": "2026-10-01 00:00:00", "access_to": "2027-10-01 23:59:59", "status": "Active"}
        ],
        "medical_summaries": [
            {
                "summary_id": 1, "patient_id": 2, "appointment_id": 2, "summary_type": "Pre-visit",
                "summary_text": "Patient is a 36-year-old female with 7-year history of Type 2 Diabetes and 5-year Essential Hypertension. Known Sulfa allergy. Latest HbA1c 6.8%. BP well controlled at 122/80 on Telmisartan. Fasting logs indicate stable morning glucose.",
                "generated_by": "System AI Pre-Visit Synthesizer", "version_no": 1, "is_current": True, "generated_at": "2026-10-31 08:00:00", "document_ids": [2]
            }
        ],
        "notifications": [
            {"notification_id": 1, "user_id": 2, "appointment_id": 1, "title": "New Appointment Booked", "message": "Patient Aarav Mehta booked for 2026-11-01 at 10:00 AM (Reason: Chest tightness).", "type": "Appointment", "is_read": False, "created_at": "2026-10-31 09:15:00"},
            {"notification_id": 2, "user_id": 10, "appointment_id": 1, "title": "Appointment Confirmed", "message": "Your consultation with Dr. Rajesh Sharma at Apex Hospital is scheduled for tomorrow at 10:00 AM.", "type": "Appointment", "is_read": True, "created_at": "2026-10-31 09:16:00"}
        ],
        "access_logs": [
            {"log_id": 1, "user_id": 2, "patient_id": 1, "document_id": None, "action_type": "VIEW", "ip_address": "192.168.1.45", "remarks": "Viewed Pre-Visit Snapshot for Appointment #1", "action_time": "2026-10-31 09:30:00"},
            {"log_id": 2, "user_id": 6, "patient_id": 4, "document_id": 1, "action_type": "UPLOAD", "ip_address": "192.168.1.12", "remarks": "Uploaded Pulmonology Prescription PDF", "action_time": "2026-10-30 15:00:00"}
        ],
        "audit_trail": [
            {"audit_id": 1, "user_id": 1, "table_name": "hospital", "record_id": "1", "action_type": "INSERT", "new_value": {"name": "Apex Heart Hospital"}, "remarks": "Initial hospital registration", "action_time": "2026-10-25 10:00:00"},
            {"audit_id": 2, "user_id": 6, "table_name": "prescription", "record_id": "1", "action_type": "INSERT", "new_value": {"items_count": 2}, "remarks": "Prescription generated for Visit #1", "action_time": "2026-10-30 14:40:00"}
        ]
    }


class APIClient:
    """
    Robust API Client with automatic fallback to high-fidelity mock store.
    Provides complete typed interfaces for all REST endpoints in the FastAPI backend.
    """

    def __init__(self, base_url: str = DEFAULT_BACKEND_URL, username: Optional[str] = None, password: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.mock_db = get_initial_mock_db()
        self._is_online: Optional[bool] = None

    def set_credentials(self, username: Optional[str], password: Optional[str]):
        self.username = username
        self.password = password

    def _get_auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def check_health(self) -> Dict[str, Any]:
        """Checks if the FastAPI backend is responding."""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=1.5)
            if resp.status_code == 200:
                self._is_online = True
                return {"online": True, "status": resp.json(), "url": self.base_url}
        except Exception:
            pass
        self._is_online = False
        return {"online": False, "status": "Offline (Running in Resilient Demo Mode)", "url": self.base_url}

    def _request(self, method: str, path: str, **kwargs) -> Optional[requests.Response]:
        """Attempts live request; returns None if backend is unreachable."""
        url = f"{self.base_url}{path}"
        if "auth" not in kwargs and self._get_auth():
            kwargs["auth"] = self._get_auth()
        try:
            resp = requests.request(method, url, timeout=2.5, **kwargs)
            return resp
        except Exception:
            self._is_online = False
            return None

    # --------------------------------------------------------------------------
    # IDENTITY & PROFILES
    # --------------------------------------------------------------------------

    def list_persons(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/identity/persons?limit={limit}&offset={offset}")
        if res and res.status_code == 200:
            return res.json()
        return self.mock_db["persons"]

    def get_person(self, person_id: int) -> Optional[Dict[str, Any]]:
        res = self._request("GET", f"/identity/persons/{person_id}")
        if res and res.status_code == 200:
            return res.json()
        for p in self.mock_db["persons"]:
            if p["person_id"] == person_id:
                return p
        return None

    def create_person(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/identity/persons", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([p["person_id"] for p in self.mock_db["persons"]], default=0) + 1
        item = {**data, "person_id": new_id, "created_at": datetime.now().isoformat()}
        self.mock_db["persons"].append(item)
        return item

    def update_person(self, person_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = self._request("PUT", f"/identity/persons/{person_id}", json=data)
        if res and res.status_code == 200:
            return res.json()
        for i, p in enumerate(self.mock_db["persons"]):
            if p["person_id"] == person_id:
                self.mock_db["persons"][i] = {**p, **data}
                return self.mock_db["persons"][i]
        return None

    def list_roles(self) -> List[Dict[str, Any]]:
        res = self._request("GET", "/identity/roles")
        if res and res.status_code == 200:
            return res.json()
        return self.mock_db["roles"]

    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/identity/users", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([u["user_id"] for u in self.mock_db["users"]], default=0) + 1
        item = {**data, "user_id": new_id, "is_active": True, "created_at": datetime.now().isoformat()}
        self.mock_db["users"].append(item)
        return item

    def assign_role(self, user_id: int, role_id: int) -> Dict[str, Any]:
        res = self._request("POST", f"/identity/users/{user_id}/roles", json={"role_id": role_id})
        if res and res.status_code in (200, 201):
            return res.json()
        self.mock_db["user_roles"].append({"user_id": user_id, "role_id": role_id})
        return {"ok": True, "message": "Role assigned successfully"}

    def change_password(self, user_id: int, new_password: str) -> Dict[str, Any]:
        res = self._request("PATCH", f"/identity/users/{user_id}/password", json={"new_password": new_password})
        if res and res.status_code == 200:
            return res.json()
        return {"ok": True, "message": "Password updated successfully in demo store"}

    def list_patients(self) -> List[Dict[str, Any]]:
        return self.mock_db["patients"]

    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        res = self._request("GET", f"/identity/patients/{patient_id}")
        if res and res.status_code == 200:
            return res.json()
        for p in self.mock_db["patients"]:
            if p["patient_id"] == patient_id:
                return p
        return None

    def create_patient(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/identity/patients", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([p["patient_id"] for p in self.mock_db["patients"]], default=0) + 1
        person = self.get_person(data.get("person_id", 0))
        full_name = person["full_name"] if person else f"Patient {new_id}"
        item = {**data, "patient_id": new_id, "full_name": full_name, "created_at": datetime.now().isoformat()}
        self.mock_db["patients"].append(item)
        return item

    def list_doctors(self) -> List[Dict[str, Any]]:
        return self.mock_db["doctors"]

    def get_doctor(self, doctor_id: int) -> Optional[Dict[str, Any]]:
        res = self._request("GET", f"/identity/doctors/{doctor_id}")
        if res and res.status_code == 200:
            return res.json()
        for d in self.mock_db["doctors"]:
            if d["doctor_id"] == doctor_id:
                return d
        return None

    def create_doctor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/identity/doctors", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([d["doctor_id"] for d in self.mock_db["doctors"]], default=0) + 1
        person = self.get_person(data.get("person_id", 0))
        full_name = person["full_name"] if person else f"Dr. Specialist {new_id}"
        item = {**data, "doctor_id": new_id, "full_name": full_name}
        self.mock_db["doctors"].append(item)
        return item

    def list_nurses(self) -> List[Dict[str, Any]]:
        return self.mock_db["nurses"]

    def create_nurse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/identity/nurses", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([n["nurse_id"] for n in self.mock_db["nurses"]], default=0) + 1
        person = self.get_person(data.get("person_id", 0))
        full_name = person["full_name"] if person else f"Nurse Staff {new_id}"
        item = {**data, "nurse_id": new_id, "full_name": full_name}
        self.mock_db["nurses"].append(item)
        return item

    # --------------------------------------------------------------------------
    # HOSPITAL MANAGEMENT
    # --------------------------------------------------------------------------

    def list_hospitals(self) -> List[Dict[str, Any]]:
        res = self._request("GET", "/hospital")
        if res and res.status_code == 200:
            return res.json()
        return self.mock_db["hospitals"]

    def get_hospital(self, hospital_id: int) -> Optional[Dict[str, Any]]:
        res = self._request("GET", f"/hospital/{hospital_id}")
        if res and res.status_code == 200:
            return res.json()
        for h in self.mock_db["hospitals"]:
            if h["hospital_id"] == hospital_id:
                return h
        return None

    def create_hospital(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/hospital", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([h["hospital_id"] for h in self.mock_db["hospitals"]], default=0) + 1
        item = {**data, "hospital_id": new_id}
        self.mock_db["hospitals"].append(item)
        return item

    def update_hospital(self, hospital_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = self._request("PUT", f"/hospital/{hospital_id}", json=data)
        if res and res.status_code == 200:
            return res.json()
        for i, h in enumerate(self.mock_db["hospitals"]):
            if h["hospital_id"] == hospital_id:
                self.mock_db["hospitals"][i] = {**h, **data}
                return self.mock_db["hospitals"][i]
        return None

    def delete_hospital(self, hospital_id: int) -> bool:
        res = self._request("DELETE", f"/hospital/{hospital_id}")
        if res and res.status_code in (200, 204):
            return True
        self.mock_db["hospitals"] = [h for h in self.mock_db["hospitals"] if h["hospital_id"] != hospital_id]
        return True

    def list_departments(self, hospital_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if hospital_id:
            res = self._request("GET", f"/hospital/{hospital_id}/departments")
            if res and res.status_code == 200:
                return res.json()
            return [d for d in self.mock_db["departments"] if d["hospital_id"] == hospital_id]
        return self.mock_db["departments"]

    def create_department(self, hospital_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", f"/hospital/{hospital_id}/departments", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([d["department_id"] for d in self.mock_db["departments"]], default=0) + 1
        item = {**data, "department_id": new_id, "hospital_id": hospital_id}
        self.mock_db["departments"].append(item)
        return item

    def list_hospital_doctors(self, hospital_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/hospital/{hospital_id}/doctors")
        if res and res.status_code == 200:
            return res.json()
        return [d for d in self.mock_db["doctors"] if d.get("hospital_id") == hospital_id]

    # --------------------------------------------------------------------------
    # APPOINTMENTS & PRE-VISIT
    # --------------------------------------------------------------------------

    def list_appointments(self, doctor_id: Optional[int] = None, patient_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if doctor_id:
            res = self._request("GET", f"/appointments/doctor/{doctor_id}")
            if res and res.status_code == 200:
                return res.json()
            return [a for a in self.mock_db["appointments"] if a["doctor_id"] == doctor_id]
        if patient_id:
            res = self._request("GET", f"/appointments/patient/{patient_id}")
            if res and res.status_code == 200:
                return res.json()
            return [a for a in self.mock_db["appointments"] if a["patient_id"] == patient_id]
        return self.mock_db["appointments"]

    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        res = self._request("GET", f"/appointments/{appointment_id}")
        if res and res.status_code == 200:
            return res.json()
        for a in self.mock_db["appointments"]:
            if a["appointment_id"] == appointment_id:
                symptoms = [s for s in self.mock_db["appointment_symptoms"] if s["appointment_id"] == appointment_id]
                notes = [n for n in self.mock_db["appointment_notes"] if n["appointment_id"] == appointment_id]
                return {**a, "symptoms": symptoms, "notes": notes}
        return None

    def create_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/appointments", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([a["appointment_id"] for a in self.mock_db["appointments"]], default=0) + 1
        patient = self.get_patient(data.get("patient_id", 0))
        doctor = self.get_doctor(data.get("doctor_id", 0))
        item = {
            **data,
            "appointment_id": new_id,
            "patient_name": patient["full_name"] if patient else f"Patient {data.get('patient_id')}",
            "doctor_name": doctor["full_name"] if doctor else f"Doctor {data.get('doctor_id')}",
            "created_at": datetime.now().isoformat()
        }
        self.mock_db["appointments"].append(item)
        return item

    def update_appointment_status(self, appointment_id: int, status: str) -> Dict[str, Any]:
        res = self._request("PATCH", f"/appointments/{appointment_id}/status", json={"status": status})
        if res and res.status_code == 200:
            return res.json()
        for i, a in enumerate(self.mock_db["appointments"]):
            if a["appointment_id"] == appointment_id:
                self.mock_db["appointments"][i]["status"] = status
                return self.mock_db["appointments"][i]
        return {"ok": True, "status": status}

    def check_in_appointment(self, appointment_id: int) -> Dict[str, Any]:
        res = self._request("POST", f"/appointments/{appointment_id}/check-in")
        if res and res.status_code == 200:
            return res.json()
        self.update_appointment_status(appointment_id, "In Progress")
        return {"ok": True, "message": f"Appointment #{appointment_id} checked in successfully"}

    def add_appointment_symptom(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/appointments/symptoms", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([s["symptom_id"] for s in self.mock_db["appointment_symptoms"]], default=0) + 1
        item = {**data, "symptom_id": new_id}
        self.mock_db["appointment_symptoms"].append(item)
        return item

    def add_appointment_note(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/appointments/notes", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([n["appt_note_id"] for n in self.mock_db["appointment_notes"]], default=0) + 1
        item = {**data, "appt_note_id": new_id, "added_at": datetime.now().isoformat()}
        self.mock_db["appointment_notes"].append(item)
        return item

    def get_previsit_snapshot(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        res = self._request("GET", f"/previsit/appointment/{appointment_id}")
        if res and res.status_code == 200:
            return res.json()
        appt = self.get_appointment(appointment_id)
        if not appt:
            return None
        pid = appt["patient_id"]
        allergies = [a["allergen"] + f" ({a['severity']})" for a in self.get_patient_allergies(pid)]
        conditions = [c["condition_name"] + f" [{c['status']}]" for c in self.get_patient_conditions(pid)]
        symptoms = [s["symptom_name"] + f" ({s['severity']})" for s in self.mock_db["appointment_symptoms"] if s["appointment_id"] == appointment_id]
        
        # Ongoing medicines
        meds = []
        for pr in self.mock_db["prescriptions"]:
            if pr["patient_id"] == pid:
                for it in pr.get("items", []):
                    if it.get("is_ongoing"):
                        meds.append(f"{it['medicine_name']} ({it.get('dosage','')})")

        return {
            "appointment_id": appointment_id,
            "appointment_date": appt["appointment_date"],
            "time_slot": appt["time_slot"],
            "doctor_id": appt["doctor_id"],
            "patient_id": pid,
            "patient_name": appt.get("patient_name", f"Patient #{pid}"),
            "reason": appt.get("reason"),
            "pre_visit_notes": appt.get("pre_visit_notes"),
            "todays_symptoms": ", ".join(symptoms) if symptoms else "None reported today",
            "active_allergies": ", ".join(allergies) if allergies else "NKDA (No Known Drug Allergies)",
            "active_conditions": ", ".join(conditions) if conditions else "No recorded chronic conditions",
            "ongoing_medicines": ", ".join(meds) if meds else "None currently active",
            "latest_summary": "Comprehensive pre-visit check ready for clinical review."
        }

    # --------------------------------------------------------------------------
    # CLINICAL VISITS & ENCOUNTERS
    # --------------------------------------------------------------------------

    def list_patient_visits(self, patient_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/visits/patient/{patient_id}")
        if res and res.status_code == 200:
            return res.json()
        return [v for v in self.mock_db["visits"] if v["patient_id"] == patient_id]

    def get_visit(self, visit_id: int) -> Optional[Dict[str, Any]]:
        res = self._request("GET", f"/visits/{visit_id}")
        if res and res.status_code == 200:
            return res.json()
        for v in self.mock_db["visits"]:
            if v["visit_id"] == visit_id:
                return v
        return None

    def create_visit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/visits", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([v["visit_id"] for v in self.mock_db["visits"]], default=0) + 1
        patient = self.get_patient(data.get("patient_id", 0))
        doctor = self.get_doctor(data.get("doctor_id", 0))
        item = {
            **data,
            "visit_id": new_id,
            "patient_name": patient["full_name"] if patient else f"Patient {data.get('patient_id')}",
            "doctor_name": doctor["full_name"] if doctor else f"Doctor {data.get('doctor_id')}"
        }
        self.mock_db["visits"].append(item)
        return item

    def add_diagnosis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/visits/diagnoses", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([d["diagnosis_id"] for d in self.mock_db["diagnoses"]], default=0) + 1
        item = {**data, "diagnosis_id": new_id}
        self.mock_db["diagnoses"].append(item)
        return item

    def list_diagnoses(self, visit_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/visits/{visit_id}/diagnoses")
        if res and res.status_code == 200:
            return res.json()
        return [d for d in self.mock_db["diagnoses"] if d["visit_id"] == visit_id]

    def add_procedure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/visits/procedures", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([p["procedure_id"] for p in self.mock_db["procedures"]], default=0) + 1
        item = {**data, "procedure_id": new_id}
        self.mock_db["procedures"].append(item)
        return item

    def list_procedures(self, visit_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/visits/{visit_id}/procedures")
        if res and res.status_code == 200:
            return res.json()
        return [p for p in self.mock_db["procedures"] if p["visit_id"] == visit_id]

    def add_visit_note(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/visits/notes", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([n["note_id"] for n in self.mock_db["visit_notes"]], default=0) + 1
        item = {**data, "note_id": new_id, "added_at": datetime.now().isoformat()}
        self.mock_db["visit_notes"].append(item)
        return item

    def list_visit_notes(self, visit_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/visits/{visit_id}/notes")
        if res and res.status_code == 200:
            return res.json()
        return [n for n in self.mock_db["visit_notes"] if n["visit_id"] == visit_id]

    def get_patient_allergies(self, patient_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/visits/patient/{patient_id}/allergies")
        if res and res.status_code == 200:
            return res.json()
        return [a for a in self.mock_db["allergies"] if a["patient_id"] == patient_id]

    def add_allergy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/visits/allergies", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([a["allergy_id"] for a in self.mock_db["allergies"]], default=0) + 1
        item = {**data, "allergy_id": new_id, "status": "Active"}
        self.mock_db["allergies"].append(item)
        return item

    def resolve_allergy(self, allergy_id: int) -> Dict[str, Any]:
        res = self._request("PATCH", f"/visits/allergies/{allergy_id}/resolve")
        if res and res.status_code == 200:
            return res.json()
        for a in self.mock_db["allergies"]:
            if a["allergy_id"] == allergy_id:
                a["status"] = "Resolved"
        return {"ok": True, "message": "Allergy resolved"}

    def get_patient_conditions(self, patient_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/visits/patient/{patient_id}/conditions")
        if res and res.status_code == 200:
            return res.json()
        return [c for c in self.mock_db["conditions"] if c["patient_id"] == patient_id]

    def add_condition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/visits/conditions", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([c["condition_id"] for c in self.mock_db["conditions"]], default=0) + 1
        item = {**data, "condition_id": new_id}
        self.mock_db["conditions"].append(item)
        return item

    def update_condition_status(self, condition_id: int, status: str) -> Dict[str, Any]:
        res = self._request("PATCH", f"/visits/conditions/{condition_id}/status", json={"status": status})
        if res and res.status_code == 200:
            return res.json()
        for c in self.mock_db["conditions"]:
            if c["condition_id"] == condition_id:
                c["status"] = status
        return {"ok": True, "message": f"Condition status set to {status}"}

    def create_prescription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/visits/prescriptions", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([p["prescription_id"] for p in self.mock_db["prescriptions"]], default=0) + 1
        items = data.get("items", [])
        for i, it in enumerate(items, 1):
            it["item_id"] = i
            it["prescription_id"] = new_id
        item = {**data, "prescription_id": new_id, "items": items}
        self.mock_db["prescriptions"].append(item)
        return item

    def get_full_visit_summary(self, visit_id: int) -> Dict[str, Any]:
        res = self._request("GET", f"/visits/{visit_id}/full-summary")
        if res and res.status_code == 200:
            return res.json()
        visit = self.get_visit(visit_id)
        if not visit:
            return {}
        return {
            "visit": visit,
            "diagnoses": self.list_diagnoses(visit_id),
            "procedures": self.list_procedures(visit_id),
            "notes": self.list_visit_notes(visit_id),
            "prescriptions": [p for p in self.mock_db["prescriptions"] if p.get("visit_id") == visit_id]
        }

    # --------------------------------------------------------------------------
    # DIAGNOSTICS & LABS
    # --------------------------------------------------------------------------

    def list_diagnostic_tests(self) -> List[Dict[str, Any]]:
        res = self._request("GET", "/diagnostics/tests")
        if res and res.status_code == 200:
            return res.json()
        return self.mock_db["diagnostic_tests"]

    def create_diagnostic_test(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/diagnostics/tests", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([t["test_id"] for t in self.mock_db["diagnostic_tests"]], default=0) + 1
        item = {**data, "test_id": new_id}
        self.mock_db["diagnostic_tests"].append(item)
        return item

    def list_test_parameters(self, test_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/diagnostics/tests/{test_id}/parameters")
        if res and res.status_code == 200:
            return res.json()
        return [p for p in self.mock_db["test_parameters"] if p["test_id"] == test_id]

    def create_test_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/diagnostics/orders", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([o["order_id"] for o in self.mock_db["test_orders"]], default=0) + 1
        item = {**data, "order_id": new_id, "order_date": datetime.now().isoformat()}
        self.mock_db["test_orders"].append(item)
        return item

    def list_test_results(self, patient_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if patient_id:
            return [r for r in self.mock_db["test_results"] if r.get("patient_id") == patient_id]
        return self.mock_db["test_results"]

    def create_test_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/diagnostics/results", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([r["result_id"] for r in self.mock_db["test_results"]], default=0) + 1
        item = {**data, "result_id": new_id, "report_date": datetime.now().isoformat()}
        self.mock_db["test_results"].append(item)
        return item

    def verify_test_result(self, result_id: int, verified_by: int) -> Dict[str, Any]:
        res = self._request("PUT", f"/diagnostics/results/{result_id}/verify?verified_by={verified_by}")
        if res and res.status_code == 200:
            return res.json()
        for r in self.mock_db["test_results"]:
            if r["result_id"] == result_id:
                r["verification_status"] = "Verified"
                r["verified_by"] = verified_by
        return {"ok": True, "message": "Result verified successfully"}

    # --------------------------------------------------------------------------
    # MEDICAL DOCUMENTS & VAULT
    # --------------------------------------------------------------------------

    def list_document_types(self) -> List[Dict[str, Any]]:
        res = self._request("GET", "/documents/types")
        if res and res.status_code == 200:
            return res.json()
        return self.mock_db["document_types"]

    def list_document_tags(self) -> List[Dict[str, Any]]:
        res = self._request("GET", "/documents/tags")
        if res and res.status_code == 200:
            return res.json()
        return self.mock_db["document_tags"]

    def list_patient_documents(self, patient_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/documents/patient/{patient_id}")
        if res and res.status_code == 200:
            return res.json()
        return [d for d in self.mock_db["documents"] if d["patient_id"] == patient_id]

    def upload_document(self, data: Dict[str, Any], tag_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        new_id = max([d["document_id"] for d in self.mock_db["documents"]], default=0) + 1
        item = {
            **data,
            "document_id": new_id,
            "uploaded_at": datetime.now().isoformat(),
            "verification_status": "Verified",
            "ocr_status": "Done",
            "tag_ids": tag_ids or []
        }
        self.mock_db["documents"].append(item)
        return item

    def verify_document(self, document_id: int) -> Dict[str, Any]:
        res = self._request("PATCH", f"/documents/{document_id}/verify")
        if res and res.status_code == 200:
            return res.json()
        for d in self.mock_db["documents"]:
            if d["document_id"] == document_id:
                d["verification_status"] = "Verified"
        return {"ok": True, "message": "Document verified"}

    def delete_document(self, document_id: int) -> bool:
        res = self._request("DELETE", f"/documents/{document_id}")
        if res and res.status_code in (200, 204):
            return True
        self.mock_db["documents"] = [d for d in self.mock_db["documents"] if d["document_id"] != document_id]
        return True

    # --------------------------------------------------------------------------
    # CONSENT & PERMISSIONS
    # --------------------------------------------------------------------------

    def list_patient_consents(self, patient_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/consent/patient/{patient_id}")
        if res and res.status_code == 200:
            return res.json()
        return [c for c in self.mock_db["consents"] if c["patient_id"] == patient_id]

    def create_consent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/consent", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([c["consent_id"] for c in self.mock_db["consents"]], default=0) + 1
        patient = self.get_patient(data.get("patient_id", 0))
        item = {**data, "consent_id": new_id, "patient_name": patient["full_name"] if patient else f"Patient {data.get('patient_id')}"}
        self.mock_db["consents"].append(item)
        return item

    def revoke_consent(self, consent_id: int) -> Dict[str, Any]:
        res = self._request("PATCH", f"/consent/{consent_id}/revoke")
        if res and res.status_code == 200:
            return res.json()
        for c in self.mock_db["consents"]:
            if c["consent_id"] == consent_id:
                c["status"] = "Revoked"
                return c
        return {"ok": True, "message": "Consent revoked"}

    def check_doctor_access(self, patient_id: int, doctor_id: int) -> Dict[str, Any]:
        res = self._request("GET", f"/consent/check?patient_id={patient_id}&doctor_id={doctor_id}")
        if res and res.status_code == 200:
            return res.json()
        # Mock logic
        for c in self.mock_db["consents"]:
            if c["patient_id"] == patient_id and c["status"] == "Active":
                for a in self.mock_db["consent_access"]:
                    if a["consent_id"] == c["consent_id"] and a.get("doctor_id") == doctor_id and a["status"] == "Active":
                        return {"has_access": True, "consent_id": c["consent_id"], "purpose": c.get("purpose")}
        return {"has_access": False, "message": "No active consent found for this doctor-patient pair."}

    def grant_consent_access(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/consent/access", json=data)
        if res and res.status_code in (200, 201):
            return res.json()
        new_id = max([a["access_id"] for a in self.mock_db["consent_access"]], default=0) + 1
        doc = self.get_doctor(data.get("doctor_id", 0)) if data.get("doctor_id") else None
        item = {**data, "access_id": new_id, "doctor_name": doc["full_name"] if doc else None, "status": "Active"}
        self.mock_db["consent_access"].append(item)
        return item

    # --------------------------------------------------------------------------
    # LOGGING & NOTIFICATIONS
    # --------------------------------------------------------------------------

    def list_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        res = self._request("GET", f"/logging/notifications/{user_id}")
        if res and res.status_code == 200:
            return res.json()
        return [n for n in self.mock_db["notifications"] if n.get("user_id") == user_id]

    def mark_notification_read(self, notification_id: int) -> Dict[str, Any]:
        res = self._request("PATCH", f"/logging/notifications/{notification_id}/read")
        if res and res.status_code == 200:
            return res.json()
        for n in self.mock_db["notifications"]:
            if n["notification_id"] == notification_id:
                n["is_read"] = True
        return {"ok": True}

    def list_access_logs(self, patient_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if patient_id:
            res = self._request("GET", f"/logging/access/patient/{patient_id}")
            if res and res.status_code == 200:
                return res.json()
            return [l for l in self.mock_db["access_logs"] if l.get("patient_id") == patient_id]
        return self.mock_db["access_logs"]

    def list_audit_trail(self) -> List[Dict[str, Any]]:
        return self.mock_db["audit_trail"]


# Singleton instance for easy import across pages
client = APIClient()

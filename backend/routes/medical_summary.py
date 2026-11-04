from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection
from sqlalchemy import text

from dependencies import get_db_connection
from queries import summary_queries as q
from schemas.medical_summary import MedicalSummaryCreate, MedicalSummaryOut

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("", response_model=MedicalSummaryOut, status_code=201)
def create(p: MedicalSummaryCreate, conn: Connection = Depends(get_db_connection)):
    data = p.model_dump(exclude={"document_ids", "document_notes"})
    if data.get("is_current"):
        q.set_previous_summaries_inactive(conn, data["patient_id"])
    sid = q.create_summary(conn, data)
    for i, did in enumerate(p.document_ids):
        note = p.document_notes[i] if p.document_notes and i < len(p.document_notes) else None
        q.link_document(conn, sid, did, note)
    return {**q.get_summary(conn, sid),
            "document_ids": q.summary_documents(conn, sid)}


@router.get("/{summary_id}", response_model=MedicalSummaryOut)
def get_one(summary_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_summary(conn, summary_id)
    if not row:
        raise HTTPException(404, "Summary not found")
    return {**row, "document_ids": q.summary_documents(conn, summary_id)}


@router.get("/patient/{patient_id}", response_model=list[MedicalSummaryOut])
def by_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    rows = q.list_by_patient(conn, patient_id)
    return [{**r, "document_ids": q.summary_documents(conn, r["summary_id"])}
            for r in rows]


@router.post("/generate/{appointment_id}", response_model=MedicalSummaryOut)
def generate_summary(appointment_id: int, conn: Connection = Depends(get_db_connection)):
    """
    Generate an intelligent Clinical Episode / Discharge Summary for the current consultation
    using Groq AI (or structured clinical fallback). Pulls real-time encounter data:
    vitals, examination, ICD-10 diagnoses, medications, procedures, and SOAP notes.
    """
    # 1. Fetch appointment, patient, doctor, and hospital details
    appt = conn.execute(text("""
        SELECT a.appointment_id, a.patient_id, a.doctor_id, a.hospital_id,
               a.appointment_date, a.time_slot, a.reason,
               p_pat.full_name AS patient_name,
               p_pat.gender,
               p_pat.date_of_birth,
               pt.blood_group,
               p_doc.full_name AS doctor_name,
               d.specialization AS doctor_specialization,
               h.name AS hospital_name
        FROM appointment a
        JOIN patient_profile pt ON a.patient_id = pt.patient_id
        JOIN person p_pat       ON pt.person_id = p_pat.person_id
        JOIN doctor_profile d   ON a.doctor_id  = d.doctor_id
        JOIN person p_doc       ON d.person_id  = p_doc.person_id
        JOIN hospital h         ON a.hospital_id = h.hospital_id
        WHERE a.appointment_id = :a
    """), {"a": appointment_id}).mappings().first()

    if not appt:
        raise HTTPException(404, f"Appointment #{appointment_id} not found")

    patient_id = appt["patient_id"]

    # 2. Fetch intake symptoms recorded for this appointment
    symptoms = conn.execute(text("""
        SELECT symptom_name, severity, notes
        FROM appointment_symptom WHERE appointment_id = :a
    """), {"a": appointment_id}).mappings().all()

    # 3. Fetch SOAP notes
    soap_notes = conn.execute(text("""
        SELECT note_text FROM appointment_note
        WHERE appointment_id = :a ORDER BY created_at DESC
    """), {"a": appointment_id}).mappings().all()

    # 4. Fetch the visit recorded for this appointment (or most recent for this patient)
    visit = conn.execute(text("""
        SELECT visit_id, visit_type, chief_complaint, vitals_summary, notes
        FROM visit WHERE appointment_id = :a
        ORDER BY visit_date DESC LIMIT 1
    """), {"a": appointment_id}).mappings().first()

    if not visit:
        visit = conn.execute(text("""
            SELECT visit_id, visit_type, chief_complaint, vitals_summary, notes
            FROM visit WHERE patient_id = :p
            ORDER BY visit_date DESC LIMIT 1
        """), {"p": patient_id}).mappings().first()

    diagnoses = []
    prescriptions = []
    procedures = []
    if visit:
        vid = visit["visit_id"]
        diagnoses = conn.execute(text("""
            SELECT diagnosis_name, diagnosis_code, diagnosis_type, notes
            FROM visit_diagnosis WHERE visit_id = :vid
        """), {"vid": vid}).mappings().all()

        prescriptions = conn.execute(text("""
            SELECT pi.medicine_name, pi.dosage, pi.frequency, pi.duration_days, pi.instructions
            FROM prescription pr
            JOIN prescription_item pi ON pr.prescription_id = pi.prescription_id
            WHERE pr.visit_id = :vid
        """), {"vid": vid}).mappings().all()

        procedures = conn.execute(text("""
            SELECT procedure_name, notes FROM visit_procedure WHERE visit_id = :vid
        """), {"vid": vid}).mappings().all()

    # 5. Build prompt for Groq AI
    chief_complaint = (visit["chief_complaint"] if visit and visit.get("chief_complaint") else appt.get("reason")) or "Clinical consultation"
    vitals = (visit["vitals_summary"] if visit and visit.get("vitals_summary") else None) or "Not recorded"
    exam_notes = (visit["notes"] if visit and visit.get("notes") else None) or "None recorded"

    prompt_lines = [
        f"Generate a professional, structured Clinical Episode & Discharge Summary for this consultation encounter.",
        "",
        f"**Patient:** {appt['patient_name']} (DOB: {appt['date_of_birth']}, Gender: {appt['gender']}, Blood Group: {appt['blood_group'] or 'Unknown'})",
        f"**Attending Physician:** Dr. {appt['doctor_name']} ({appt['doctor_specialization'] or 'Specialist'})",
        f"**Healthcare Facility:** {appt['hospital_name']}",
        f"**Date:** {appt['appointment_date']}",
        f"**Chief Complaint:** {chief_complaint}",
        f"**Vitals:** {vitals}",
        f"**Clinical Examination:** {exam_notes}",
        "",
        "**Diagnoses Recorded Today:**",
    ]

    if diagnoses:
        for d in diagnoses:
            prompt_lines.append(f"  - {d['diagnosis_name']} (Code: {d['diagnosis_code'] or 'N/A'}, Type: {d['diagnosis_type']}) — {d['notes'] or ''}")
    else:
        prompt_lines.append("  - None formally coded")

    prompt_lines.append("\n**Medications Prescribed Today:**")
    if prescriptions:
        for rx in prescriptions:
            prompt_lines.append(f"  - {rx['medicine_name']} ({rx['dosage'] or 'Standard dose'}, {rx['frequency'] or 'As directed'}, {rx['duration_days'] or 5} days). {rx['instructions'] or ''}")
    else:
        prompt_lines.append("  - None prescribed")

    if procedures:
        prompt_lines.append("\n**Procedures Performed:**")
        for proc in procedures:
            prompt_lines.append(f"  - {proc['procedure_name']}: {proc['notes'] or ''}")

    if soap_notes:
        prompt_lines.append("\n**Physician SOAP Notes:**")
        for sn in soap_notes:
            prompt_lines.append(f"  {sn['note_text']}")

    prompt_text = "\n".join(prompt_lines)

    # 6. Call Groq AI or use fallback
    summary_text = None
    generated_by = "AI"

    try:
        from routes.ai import _call_groq
        ai_res = _call_groq(prompt_text)
        if ai_res and ai_res.get("summary"):
            summary_text = ai_res["summary"]
    except Exception:
        # Fallback structured generation
        generated_by = "System"
        diag_str = ", ".join([d["diagnosis_name"] for d in diagnoses]) if diagnoses else "Clinical observation"
        rx_str = ", ".join([f"{r['medicine_name']} ({r['dosage'] or ''})" for r in prescriptions]) if prescriptions else "None"
        summary_text = (
            f"**Patient:** {appt['patient_name']} | **Doctor:** Dr. {appt['doctor_name']} ({appt['doctor_specialization'] or 'Physician'})\n"
            f"**Facility:** {appt['hospital_name']} | **Date:** {appt['appointment_date']}\n\n"
            f"**Chief Complaint:** {chief_complaint}\n"
            f"**Vitals:** {vitals}\n"
            f"**Diagnosis:** {diag_str}\n"
            f"**Prescriptions:** {rx_str}\n"
            f"**Clinical Plan:** Follow up as advised. Seek emergency care if symptoms worsen."
        )

    # 7. Set previous patient summaries to is_current = FALSE
    q.set_previous_summaries_inactive(conn, patient_id)

    # 8. Save the newly generated episode summary
    data = {
        "patient_id": patient_id,
        "appointment_id": appointment_id,
        "summary_type": "Discharge",
        "summary_text": summary_text,
        "generated_by": generated_by,
        "version_no": 1,
        "is_current": True
    }
    sid = q.create_summary(conn, data)
    return {**q.get_summary(conn, sid), "document_ids": []}

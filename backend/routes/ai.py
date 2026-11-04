"""
Backend route: /ai  — Groq-powered clinical summarization endpoints.

POST /ai/summarize          - Free-text clinical NLP summary
POST /ai/summarize/visit    - Summarize a full visit (visit_id) using DB data
POST /ai/summarize/patient  - Summarize a patient's entire history (patient_id)
GET  /ai/config             - Check if Groq key is configured (redacted)
PUT  /ai/config/key         - Update the Groq API key at runtime (stored in .env)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional

from dependencies import get_db_connection
from config import settings

router = APIRouter(prefix="/ai", tags=["ai"])

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class SummarizeRequest(BaseModel):
    text: str
    context: Optional[str] = "clinical"       # hint for the system prompt
    model: Optional[str] = None               # override model per-request


class VisitSummarizeRequest(BaseModel):
    visit_id: int
    model: Optional[str] = None


class PatientSummarizeRequest(BaseModel):
    patient_id: int
    model: Optional[str] = None


class GroqKeyUpdate(BaseModel):
    api_key: str


class SummarizeResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    summary: str
    model_used: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CLINICAL_SYSTEM_PROMPT = (
    "You are an expert clinical AI assistant for a hospital EHR system. "
    "Your task is to produce concise, structured medical summaries. "
    "Always use medical terminology where appropriate. "
    "Format your response in clear sections using markdown headings. "
    "Do NOT fabricate diagnoses or medications not present in the input."
)


def _groq_client():
    """Return a Groq client, raising 503 if the key is not set."""
    from groq import Groq
    key = settings.GROQ_API_KEY
    if not key or key.strip() == "":
        raise HTTPException(
            status_code=503,
            detail="Groq API key is not configured. Set GROQ_API_KEY in backend/.env or via PUT /ai/config/key"
        )
    return Groq(api_key=key)


def _call_groq(user_message: str, model: Optional[str] = None, system: str = CLINICAL_SYSTEM_PROMPT) -> dict:
    """Call Groq chat completions and return {summary, model_used, usage}."""
    client = _groq_client()
    chosen_model = model or settings.GROQ_MODEL

    completion = client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    return {
        "summary":           completion.choices[0].message.content,
        "model_used":        completion.model,
        "prompt_tokens":     completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/summarize", response_model=SummarizeResponse)
def summarize_text(req: SummarizeRequest):
    """Summarize arbitrary clinical free-text using Groq LLM."""
    prompt = (
        f"Summarize the following {req.context} notes into a structured clinical report:\n\n"
        f"{req.text}"
    )
    result = _call_groq(prompt, model=req.model)
    return SummarizeResponse(**result)


@router.post("/summarize/visit", response_model=SummarizeResponse)
def summarize_visit(req: VisitSummarizeRequest, conn: Connection = Depends(get_db_connection)):
    """Fetch a full visit record from the DB and generate an AI summary with Groq."""
    visit_row = conn.execute(text("""
        SELECT v.visit_id, v.visit_date, v.visit_type, v.chief_complaint,
               v.vitals_summary, v.notes,
               p.full_name AS patient_name,
               pd.full_name AS doctor_name,
               h.name AS hospital_name
        FROM visit v
        JOIN patient_profile pt ON v.patient_id = pt.patient_id
        JOIN person p           ON pt.person_id = p.person_id
        JOIN doctor_profile d   ON v.doctor_id  = d.doctor_id
        JOIN person pd          ON d.person_id  = pd.person_id
        JOIN hospital h         ON v.hospital_id = h.hospital_id
        WHERE v.visit_id = :vid
    """), {"vid": req.visit_id}).mappings().first()

    if not visit_row:
        raise HTTPException(404, f"Visit #{req.visit_id} not found")

    # Collect diagnoses
    diagnoses = conn.execute(text("""
        SELECT diagnosis_name, diagnosis_code, diagnosis_type, notes
        FROM visit_diagnosis WHERE visit_id = :vid
    """), {"vid": req.visit_id}).mappings().all()

    # Collect prescriptions
    prescriptions = conn.execute(text("""
        SELECT pi.medicine_name, pi.dosage, pi.frequency, pi.duration_days, pi.instructions
        FROM prescription pr
        JOIN prescription_item pi ON pr.prescription_id = pi.prescription_id
        WHERE pr.visit_id = :vid
    """), {"vid": req.visit_id}).mappings().all()

    # Collect procedures
    procedures = conn.execute(text("""
        SELECT procedure_name, notes FROM visit_procedure WHERE visit_id = :vid
    """), {"vid": req.visit_id}).mappings().all()

    # Build prompt text
    lines = [
        f"**Patient:** {visit_row['patient_name']}",
        f"**Doctor:** Dr. {visit_row['doctor_name']}",
        f"**Hospital:** {visit_row['hospital_name']}",
        f"**Date:** {visit_row['visit_date']}",
        f"**Visit Type:** {visit_row['visit_type']}",
        f"**Chief Complaint:** {visit_row['chief_complaint'] or 'N/A'}",
        f"**Vitals:** {visit_row['vitals_summary'] or 'Not recorded'}",
        f"**Clinical Notes:** {visit_row['notes'] or 'None'}",
        "",
        "**Diagnoses:**",
    ]
    if diagnoses:
        for d in diagnoses:
            lines.append(f"  - {d['diagnosis_name']} (Code: {d['diagnosis_code'] or 'N/A'}, Type: {d['diagnosis_type']}) — {d['notes'] or ''}")
    else:
        lines.append("  None recorded")

    lines.append("\n**Prescriptions:**")
    if prescriptions:
        for rx in prescriptions:
            lines.append(f"  - {rx['medicine_name']} {rx['dosage']} × {rx['frequency']} for {rx['duration_days']} days. {rx['instructions'] or ''}")
    else:
        lines.append("  None issued")

    lines.append("\n**Procedures:**")
    if procedures:
        for p in procedures:
            lines.append(f"  - {p['procedure_name']}: {p['notes'] or ''}")
    else:
        lines.append("  None performed")

    prompt = (
        "Generate a comprehensive discharge/episode clinical summary for the following visit data:\n\n"
        + "\n".join(lines)
    )
    result = _call_groq(prompt, model=req.model)
    return SummarizeResponse(**result)


@router.post("/summarize/patient", response_model=SummarizeResponse)
def summarize_patient(req: PatientSummarizeRequest, conn: Connection = Depends(get_db_connection)):
    """Generate a longitudinal patient health summary using Groq."""
    patient_row = conn.execute(text("""
        SELECT p.full_name, p.email, p.date_of_birth, p.gender, pt.blood_group,
               pt.abha_linked, pt.emergency_contact_name, pt.emergency_contact_phone
        FROM patient_profile pt
        JOIN person p ON pt.person_id = p.person_id
        WHERE pt.patient_id = :pid
    """), {"pid": req.patient_id}).mappings().first()

    if not patient_row:
        raise HTTPException(404, f"Patient #{req.patient_id} not found")

    conditions = conn.execute(text("""
        SELECT condition_name, icd_code, condition_type, onset_date, status
        FROM patient_condition WHERE patient_id = :pid ORDER BY onset_date DESC
    """), {"pid": req.patient_id}).mappings().all()

    allergies = conn.execute(text("""
        SELECT allergen, reaction, severity, status FROM allergy WHERE patient_id = :pid
    """), {"pid": req.patient_id}).mappings().all()

    recent_visits = conn.execute(text("""
        SELECT visit_date, visit_type, chief_complaint, vitals_summary
        FROM visit WHERE patient_id = :pid ORDER BY visit_date DESC LIMIT 5
    """), {"pid": req.patient_id}).mappings().all()

    summaries = conn.execute(text("""
        SELECT summary_text FROM medical_summary
        WHERE patient_id = :pid AND is_current = 1
        ORDER BY generated_at DESC LIMIT 3
    """), {"pid": req.patient_id}).mappings().all()

    abha_status = "Linked" if patient_row["abha_linked"] else "Not Linked"
    lines = [
        f"**Patient:** {patient_row['full_name']}",
        f"**DOB:** {patient_row['date_of_birth']}  |  **Gender:** {patient_row['gender']}  |  **Blood Group:** {patient_row['blood_group'] or 'Unknown'}",
        f"**ABHA:** {abha_status}  |  **Emergency Contact:** {patient_row['emergency_contact_name'] or 'N/A'} ({patient_row['emergency_contact_phone'] or 'N/A'})",
        "",
        "**Active Conditions:**",
    ]
    if conditions:
        for c in conditions:
            lines.append(f"  - {c['condition_name']} (ICD: {c['icd_code'] or 'N/A'}, Type: {c['condition_type']}, Status: {c['status']}, Onset: {c['onset_date'] or 'N/A'})")
    else:
        lines.append("  None on record")

    lines.append("\n**Known Allergies:**")
    if allergies:
        for a in allergies:
            lines.append(f"  - {a['allergen']}: {a['reaction']} (Severity: {a['severity']})")
    else:
        lines.append("  None reported")

    lines.append("\n**Recent Visits (last 5):**")
    if recent_visits:
        for v in recent_visits:
            lines.append(f"  - {v['visit_date']} [{v['visit_type']}]: {v['chief_complaint'] or 'N/A'} | Vitals: {v['vitals_summary'] or 'N/A'}")
    else:
        lines.append("  No visit history")

    if summaries:
        lines.append("\n**Previous Medical Summaries:**")
        for s in summaries:
            lines.append(f"  ---\n  {s['summary_text'][:600]}...")

    prompt = (
        "Generate a comprehensive longitudinal patient health summary suitable for a clinical handover, "
        "based on the following patient records:\n\n"
        + "\n".join(lines)
    )
    result = _call_groq(prompt, model=req.model)
    return SummarizeResponse(**result)


@router.get("/config")
def get_ai_config():
    """Return current AI configuration (key redacted)."""
    key = settings.GROQ_API_KEY
    configured = bool(key and key.strip())
    masked = (key[:8] + "..." + key[-4:]) if configured and len(key) > 12 else ("****" if configured else "")
    return {
        "groq_configured": configured,
        "api_key_preview": masked,
        "model": settings.GROQ_MODEL,
    }


@router.put("/config/key", status_code=200)
def update_groq_key(payload: GroqKeyUpdate):
    """
    Update the Groq API key at runtime by writing it to backend/.env.
    The server must be restarted (or the settings reloaded) for it to take effect
    on new processes; we also mutate the in-memory settings object immediately.
    """
    from pathlib import Path
    env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
    if not env_path.exists():
        # Fallback: look next to this file
        env_path = Path(__file__).resolve().parent / ".env"

    new_key = payload.api_key.strip()
    if not new_key:
        raise HTTPException(400, "API key cannot be empty")

    # Read existing lines and update or append GROQ_API_KEY
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    updated = False
    for i, line in enumerate(lines):
        if line.startswith("GROQ_API_KEY="):
            lines[i] = f"GROQ_API_KEY={new_key}"
            updated = True
            break
    if not updated:
        lines.append(f"GROQ_API_KEY={new_key}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Mutate in-memory settings immediately (no restart needed for current process)
    settings.GROQ_API_KEY = new_key

    return {"message": "Groq API key updated successfully. Active immediately.", "model": settings.GROQ_MODEL}

"""
Frontend AI engine — routes all AI summarization through the backend /ai/* endpoints,
which call the Groq LLM. Falls back to a lightweight mock when the backend is unavailable
or the Groq key is not yet configured.
"""

import re
import requests
from typing import Optional

BACKEND_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------------------------
# Backend-powered (Groq) helpers
# ---------------------------------------------------------------------------

def _post_ai(endpoint: str, payload: dict) -> Optional[str]:
    """
    POST to a backend /ai/* endpoint. Returns the summary string on success,
    or None on network/key error so the caller can fall back gracefully.
    """
    try:
        resp = requests.post(f"{BACKEND_URL}/ai/{endpoint}", json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("summary", "")
        elif resp.status_code == 503:
            return None   # Groq key not configured — caller shows setup hint
        else:
            return None
    except Exception:
        return None


def summarize_text(text: str, context: str = "clinical", model: Optional[str] = None) -> str:
    """
    Send free-text clinical notes to Groq via the backend for summarization.
    Returns the AI summary markdown, or falls back to the mock engine.
    """
    result = _post_ai("summarize", {"text": text, "context": context, "model": model})
    if result is not None:
        return result
    return generate_mock_summary(text)


def summarize_visit(visit_id: int, model: Optional[str] = None) -> str:
    """Generate a Groq summary for a specific visit (fetches DB data via backend)."""
    result = _post_ai("summarize/visit", {"visit_id": visit_id, "model": model})
    if result is not None:
        return result
    return "⚠️ Could not generate visit summary. Check your Groq API key configuration."


def summarize_patient(patient_id: int, model: Optional[str] = None) -> str:
    """Generate a longitudinal Groq summary for a patient (fetches DB data via backend)."""
    result = _post_ai("summarize/patient", {"patient_id": patient_id, "model": model})
    if result is not None:
        return result
    return "⚠️ Could not generate patient summary. Check your Groq API key configuration."


def get_ai_config() -> dict:
    """Fetch the current AI/Groq configuration status from the backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/ai/config", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {"groq_configured": False, "api_key_preview": "", "model": ""}


def save_groq_api_key(api_key: str) -> tuple[bool, str]:
    """
    Save a new Groq API key via the backend (writes to .env and updates in-memory settings).
    Returns (success: bool, message: str).
    """
    try:
        resp = requests.put(f"{BACKEND_URL}/ai/config/key", json={"api_key": api_key}, timeout=10)
        if resp.status_code == 200:
            return True, resp.json().get("message", "Key saved successfully.")
        else:
            detail = resp.json().get("detail", "Unknown error")
            return False, f"Backend error: {detail}"
    except Exception as e:
        return False, f"Connection error: {e}"


# ---------------------------------------------------------------------------
# Mock / Fallback engine (used when Groq key not set or backend unreachable)
# ---------------------------------------------------------------------------

def generate_mock_summary(text: str) -> str:
    """
    Lightweight mock that simulates AI analysis.
    Used as a fallback when the Groq backend is unavailable.
    """
    if not text:
        return "No clinical text provided to analyze."

    symptoms = re.findall(r'(pain|cough|fever|nausea|dizziness|fatigue)', text, re.IGNORECASE)
    unique_symptoms = list(set([s.lower() for s in symptoms]))

    summary = "### :material/neurology: AI Clinical Analysis *(Mock — Groq key not configured)*\n"
    summary += f"**Analyzed Text Length:** {len(text)} characters\n\n"

    if unique_symptoms:
        summary += "**Identified Potential Symptoms:**\n"
        for s in unique_symptoms:
            summary += f"- {s.title()}\n"
    else:
        summary += "No obvious symptom keywords found. Manual review recommended.\n"

    summary += "\n**Recommendation:** Correlate with patient's pre-visit snapshot and lab results."
    summary += "\n\n> 💡 **Tip:** Configure your Groq API key in Admin → AI Assistant → Settings to enable real AI summaries."
    return summary

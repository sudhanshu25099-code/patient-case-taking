import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth
from config import settings
from routes import (
    identity, hospital, appointments, visits_clinical, diagnostics,
    documents, consent, medical_summary, logging_notifications, previsit,
)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

for r in (identity, hospital, appointments, visits_clinical, diagnostics,
          documents, consent, medical_summary, logging_notifications, previsit):
    app.include_router(r.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

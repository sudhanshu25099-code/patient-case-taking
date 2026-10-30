from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import (
    identity, hospital, appointments, visits_clinical, diagnostics,
    documents, consent, medical_summary, logging_notifications, previsit,
)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

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
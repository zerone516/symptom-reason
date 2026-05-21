"""FastAPI entrypoint. SSE streaming endpoint for the agent pipeline."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

# Load .env from the backend dir
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .pipeline import run_pipeline  # noqa: E402
from .llm import load_config  # noqa: E402


app = FastAPI(
    title="SymptomReason API",
    description="Multi-agent medical reasoning pipeline. Informational only — not medical advice.",
    version="1.0.0",
)


# CORS
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


class ConsultRequest(BaseModel):
    symptoms: str = Field(..., min_length=3, max_length=4000)
    age: int | None = Field(default=None, ge=0, le=120)
    sex: str | None = Field(default=None, max_length=20)
    duration: str | None = Field(default=None, max_length=120)
    context: str | None = Field(default=None, max_length=2000)


@app.get("/")
def root():
    cfg = load_config()
    return {
        "service": "SymptomReason",
        "status": "ok",
        "provider": cfg.provider,
        "model": cfg.model,
        "disclaimer": "This service is informational only. It is not medical advice.",
    }


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/config")
def config():
    cfg = load_config()
    return {"provider": cfg.provider, "model": cfg.model}


@app.post("/api/consult")
async def consult(req: ConsultRequest):
    """Run the agent pipeline and stream progress as SSE."""
    user_input = req.model_dump()

    async def gen():
        async for chunk in run_pipeline(user_input):
            yield chunk

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # nginx
            "Connection": "keep-alive",
        },
    )


@app.get("/api/examples")
def examples():
    """Pre-baked symptom examples for the demo. No real PII."""
    return JSONResponse([
        {
            "title": "Persistent dry cough",
            "symptoms": "Persistent dry cough for 3 weeks, occasional shortness of breath when climbing stairs. No fever. Mild fatigue.",
            "age": 34,
            "sex": "female",
            "duration": "3 weeks",
            "context": "Non-smoker. No known allergies. No recent travel.",
        },
        {
            "title": "Sudden severe headache",
            "symptoms": "Sudden severe headache that started 1 hour ago, described as 'worst headache of my life'. Some neck stiffness. Mild nausea.",
            "age": 41,
            "sex": "male",
            "duration": "1 hour",
            "context": "Hypertension. Currently on lisinopril.",
        },
        {
            "title": "Fatigue and weight gain",
            "symptoms": "Increasing fatigue over 2 months. Cold intolerance. Weight gain ~5kg without diet changes. Dry skin. Constipation.",
            "age": 52,
            "sex": "female",
            "duration": "2 months",
            "context": "Family history of thyroid disease.",
        },
    ])

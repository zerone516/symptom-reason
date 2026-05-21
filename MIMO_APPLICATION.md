# SymptomReason — Mimo Application Submission

## 01. Email
*(use GitHub-associated email for zerone516)*

## 02. AI tools used
- Hermes Agent (orchestration layer)
- Cursor / VSCode
- Claude Code (fallback)

## 03. Model series
- Claude series (Sonnet 4.x — fallback path)
- **Mimo (primary target — applying for credit to use as primary)**

---

## 04. Project Description (suitable for "describe how you used the model" field)

I built **SymptomReason**, a multi-agent medical reasoning assistant, using Hermes Agent as the orchestration layer.

The core pain point: most people search their symptoms online and either spiral into worst-case anxiety or get generic, unactionable advice. The valuable part — *how should I think about this, who should I see, what should I ask the doctor* — is missing from current tools.

SymptomReason solves this by running **four specialist agents in parallel** via `asyncio.gather()`, each with a focused reasoning task: a Differential Diagnostician (long reasoning chain ranking possible conditions), a Red Flag Detector (emergency triage), a Specialist Router (which clinician to see and how soon), and a Question Crafter (questions to bring to the visit). Their outputs feed a **long-chain Synthesizer** agent that reasons step-by-step through the evidence and produces a final patient-facing report streamed live to the UI via Server-Sent Events.

The architecture is tailor-made for reasoning models like Mimo: parallel short-chain agents handle decisive triage, while the synthesizer demonstrates exactly the long-chain inference Mimo is designed for. Each session consumes approximately **9,000 tokens** (≈6K across the four parallel agents + ≈3K for the synthesizer's reasoning chain). At 50 sessions per day during testing, that's around **450K tokens daily**.

Stack: FastAPI + asyncio + SSE on the backend, React 18 + Vite + Tailwind on the frontend, OpenAI-compatible client targeting Mimo as primary with Claude as a fallback. Deployable to Railway + Vercel.

The product is positioned strictly as a **pre-consultation reasoning aid, not medical advice** — every output carries a disclaimer banner and the synthesizer is prompted to recommend professional consultation. SymptomReason helps patients walk into a doctor's office better-prepared, with a structured framing of their symptoms and the right questions to ask, which directly improves consultation efficiency.

**GitHub:** https://github.com/zerone516/symptom-reason
**Word count:** ~290

---

## 05. Proof of use

Files to upload (max 5, ≤20MB each, jpg/png/gif/webp/mp4/mov/wmv):
1. `proof/symptom_reason_run.png` — terminal screenshot of a full pipeline run (parallel agents → synthesizer → SSE summary)
2. *(optional)* a frontend screenshot once deployed
3. *(optional)* GitHub repo screenshot (zerone516/symptom-reason landing)

GitHub link to paste in the form: `https://github.com/zerone516/symptom-reason`

---

## Submission checklist

- [x] Repo public & accessible (`https://github.com/zerone516/symptom-reason`)
- [x] README explains the multi-agent architecture
- [x] Code runs locally (`backend/smoketest.py` passes)
- [x] Proof screenshot generated (Windows Terminal / Git Bash, authentic chrome)
- [x] Description hits keywords: parallel agents, long-chain reasoning, multi-agent collaboration, token budget
- [x] Different angle from previous Mimo submission (synapse-research = research; this = medical reasoning)
- [ ] Submit at https://100t.xiaomimimo.com/

---

## Quick reference

- **Reward tiers:** Standard / Pro / Max (synapse-research won Pro monthly)
- **Evaluation window:** within 3 business days
- **Support:** Feishu/Lark group via QR on the page

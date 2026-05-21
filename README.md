# SymptomReason 🩺

> Multi-agent medical reasoning assistant. **Informational only — not medical advice.**

SymptomReason is an AI-powered triage and pre-consultation assistant that helps users understand their symptoms before seeing a doctor. It uses **4 specialized agents running in parallel**, followed by a **long-chain synthesizer** that combines their reasoning into a structured report.

## Why this exists

Most people Google their symptoms and get either a panic-inducing list of worst cases or generic advice. The actual valuable thing — *"how should I think about this, who should I see, what should I ask them"* — is missing.

SymptomReason fills that gap. It is **not a diagnosis tool**. It is a **reasoning companion** that helps users prepare for a real medical consultation.

## Architecture

```
                    ┌──────────────────────────┐
                    │  User input (symptoms,   │
                    │  age, context, history)  │
                    └────────────┬─────────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  │              │              │
              ┌───▼───┐     ┌────▼────┐    ┌────▼────┐    ┌─────────┐
              │ DDx   │     │ RedFlag │    │Specialist│    │Question │
              │ Agent │     │  Agent  │    │  Router  │    │ Crafter │
              └───┬───┘     └────┬────┘    └────┬────┘    └────┬────┘
                  │              │              │              │
                  └──────────────┴──────────────┴──────────────┘
                                 │
                          asyncio.gather()  (parallel)
                                 │
                       ┌─────────▼──────────┐
                       │   Synthesizer      │
                       │   (long-chain)     │
                       └─────────┬──────────┘
                                 │
                          SSE stream → frontend
```

### The 4 Agents

| Agent | Job | Reasoning depth |
|-------|-----|-----------------|
| **DifferentialDx** | Generate ranked list of possible conditions with probability + reasoning | Long-chain |
| **RedFlag** | Detect emergency signals (cardiac, neurological, sepsis) → triage urgency | Short-chain (decisive) |
| **SpecialistRouter** | Map symptom pattern to medical specialty + urgency tier | Mid-chain |
| **QuestionCrafter** | Generate questions the user should ask their doctor | Mid-chain |

### Synthesizer

Combines the 4 agent outputs into:
- **Triage banner** (ER / urgent / routine / self-care)
- **Differential summary** (top 3 possibilities with plain-language reasoning)
- **Specialist recommendation** with urgency window
- **Print-ready prep sheet** for the doctor visit

## Tech stack

- **Backend:** FastAPI + asyncio + Server-Sent Events
- **Frontend:** React 18 + Vite + TailwindCSS
- **LLM:** Mimo (primary, via OpenAI-compatible API) + Claude fallback
- **Orchestration:** Hermes Agent (during development)
- **Deploy:** Railway (backend) + Vercel (frontend)

## Token usage estimate

A single consultation flow:
- 4 parallel agents × ~1,500 tokens = **6,000 tokens**
- Synthesizer (long-chain) = **~3,000 tokens**
- Total per session = **~9,000 tokens**

At 50 sessions/day during testing = **~450K tokens/day**.

## Disclaimer

SymptomReason is **not a substitute for professional medical advice, diagnosis, or treatment.** Always seek the advice of your physician or other qualified health provider. If you think you may have a medical emergency, **call your local emergency services immediately.**

## Local dev

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # fill in MIMO_API_KEY
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## License

MIT

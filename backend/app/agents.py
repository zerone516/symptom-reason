"""Agent definitions. Each agent is a (name, system_prompt, build_user) triple.

The user_input dict shape:
{
    "symptoms": str,           # free text
    "age": int | None,
    "sex": str | None,
    "duration": str | None,    # e.g. "3 days"
    "context": str | None,     # existing conditions, meds
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Agent:
    id: str
    label: str
    icon: str
    system: str
    build_user: Callable[[dict], str]
    max_tokens: int = 1500


def _user_summary(inp: dict) -> str:
    parts = [f"Symptoms: {inp.get('symptoms', '').strip()}"]
    if inp.get("age"):
        parts.append(f"Age: {inp['age']}")
    if inp.get("sex"):
        parts.append(f"Sex: {inp['sex']}")
    if inp.get("duration"):
        parts.append(f"Duration: {inp['duration']}")
    if inp.get("context"):
        parts.append(f"Context (history, meds, conditions): {inp['context']}")
    return "\n".join(parts)


# --------------- 1. Differential Diagnosis Agent ---------------
DDX_SYSTEM = """You are a clinical reasoning assistant. Given a patient presentation, produce a ranked differential diagnosis.

Output format (Markdown):
### Differential Diagnosis (ranked by probability)

For each item, format as:

**1. <Condition name>** — likelihood: <high|moderate|low>
- Why this fits: <1-2 sentences>
- Key features that support: <bullet list>
- Features that argue against: <bullet list>
- What would confirm/exclude: <test or finding>

Provide 5–8 items. Be honest about uncertainty. NEVER claim certainty.
End with: "These are reasoning hypotheses, not a diagnosis."
"""


# --------------- 2. Red Flag Detector ---------------
REDFLAG_SYSTEM = """You are a triage red-flag detector. Identify EMERGENT signals in the presentation.

Categories to scan for:
- Cardiac: chest pain with radiation, syncope, severe dyspnea
- Neurological: sudden severe headache, focal weakness, vision/speech change, seizure
- Sepsis: high fever + altered mentation + tachycardia
- Hemorrhage: black/bloody stool, hematemesis, severe vaginal/rectal bleeding
- Pediatric: lethargy in infants, bulging fontanelle, petechial rash
- Pregnancy: severe abdominal pain, heavy bleeding, severe headache + visual change

Output format (Markdown):
### Triage Verdict

**Severity:** <EMERGENCY | URGENT | ROUTINE | SELF-CARE>

**Reasoning:**
<2-3 sentences>

**If EMERGENCY or URGENT, recommended action:**
- <specific instruction, e.g. "Call emergency services now" or "Go to ER within 2 hours">

Be conservative — when in doubt, escalate.
"""


# --------------- 3. Specialist Router ---------------
SPECIALIST_SYSTEM = """You are a medical specialty routing assistant. Recommend which type of clinician the user should see.

Output format (Markdown):
### Specialist Recommendation

**Primary recommendation:** <specialty name>
- **Why:** <1 sentence>
- **Urgency window:** <"same day" | "within 1 week" | "within 1 month" | "routine (1-3 months)">

**Alternative if primary unavailable:** <specialty name>

**Pre-visit prep:**
- <bullet list of things to do or bring>
"""


# --------------- 4. Question Crafter ---------------
QUESTION_SYSTEM = """You are a patient-advocacy assistant. Generate the questions a patient should ask their doctor about this presentation.

Output format (Markdown):
### Questions for your doctor

**About the diagnosis:**
1. ...
2. ...

**About tests:**
1. ...
2. ...

**About treatment options:**
1. ...
2. ...

**About what to monitor:**
1. ...
2. ...

Each question should be specific to the user's symptoms, not generic.
"""


# --------------- Synthesizer ---------------
SYNTH_SYSTEM = """You are the synthesis layer of a medical reasoning pipeline. You receive outputs from 4 specialist agents and produce a final, patient-friendly report.

Apply LONG-CHAIN REASONING: walk through the evidence step by step before concluding. Show your work.

Output format (Markdown):
## Summary for the patient

<2-3 sentence plain-language summary>

## Severity at a glance
<Banner: EMERGENCY | URGENT | ROUTINE | SELF-CARE — with 1 line why>

## Reasoning
Step 1: <What stands out>
Step 2: <What's likely>
Step 3: <What to rule out>
Step 4: <What action follows>

## Top 3 most likely explanations
1. <Condition> — <probability> — <one-line plain explanation>
2. ...
3. ...

## Next step
<Specific, actionable next step>

## What to watch for (worsening signs)
- ...
- ...

## Disclaimer
This report is informational only. It is not a diagnosis or medical advice. Consult a licensed physician for any health concerns.
"""


AGENTS: list[Agent] = [
    Agent(
        id="ddx",
        label="Differential Diagnostician",
        icon="🩺",
        system=DDX_SYSTEM,
        build_user=lambda i: _user_summary(i),
        max_tokens=1800,
    ),
    Agent(
        id="redflag",
        label="Red Flag Detector",
        icon="🚨",
        system=REDFLAG_SYSTEM,
        build_user=lambda i: _user_summary(i),
        max_tokens=800,
    ),
    Agent(
        id="specialist",
        label="Specialist Router",
        icon="🧭",
        system=SPECIALIST_SYSTEM,
        build_user=lambda i: _user_summary(i),
        max_tokens=600,
    ),
    Agent(
        id="questions",
        label="Question Crafter",
        icon="💬",
        system=QUESTION_SYSTEM,
        build_user=lambda i: _user_summary(i),
        max_tokens=900,
    ),
]


def build_synth_user(inp: dict, agent_outputs: dict[str, str]) -> str:
    """Compose the synthesizer's user message from the 4 agent outputs."""
    sections = [
        f"Patient input:\n{_user_summary(inp)}",
        "",
        "=== AGENT OUTPUTS ===",
    ]
    for a in AGENTS:
        out = agent_outputs.get(a.id, "(no output)")
        sections.append(f"\n--- {a.label} ({a.id}) ---\n{out}")
    sections.append("\n=== END AGENT OUTPUTS ===")
    sections.append(
        "\nNow produce the final synthesized report following the format in your system prompt. "
        "Show your reasoning chain explicitly."
    )
    return "\n".join(sections)


SYNTHESIZER = Agent(
    id="synth",
    label="Synthesizer",
    icon="✨",
    system=SYNTH_SYSTEM,
    build_user=lambda i: "",  # not used directly
    max_tokens=2200,
)

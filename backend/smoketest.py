"""Sanity test: run the pipeline in demo mode and print the SSE stream."""
import asyncio
import os
import sys
from pathlib import Path

# Ensure no API key so demo mode kicks in
os.environ.pop("MIMO_API_KEY", None)
os.environ.pop("ANTHROPIC_API_KEY", None)

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.pipeline import run_pipeline  # noqa: E402


async def main():
    user = {
        "symptoms": "Persistent dry cough for 3 weeks, mild shortness of breath when climbing stairs.",
        "age": 34,
        "sex": "female",
        "duration": "3 weeks",
        "context": "Non-smoker, no known allergies.",
    }
    events = 0
    async for chunk in run_pipeline(user):
        events += 1
        if events <= 8 or events % 20 == 0:
            line = chunk.strip().splitlines()[-1] if chunk.strip() else ""
            print(f"[{events:03d}] {line[:140]}")
    print(f"\nTotal SSE events emitted: {events}")
    assert events > 0, "Pipeline produced no events"
    print("[OK] Smoke test passed")


if __name__ == "__main__":
    asyncio.run(main())

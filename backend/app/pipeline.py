"""Pipeline: run the 4 agents in parallel, then synthesize. Streams progress over SSE."""
from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncIterator

from .agents import AGENTS, SYNTHESIZER, build_synth_user
from .llm import LLMClient


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _run_agent(client: LLMClient, agent, user_input: dict, queue: asyncio.Queue):
    """Run one agent, push its tokens onto the shared queue tagged by agent id."""
    started = time.time()
    await queue.put(("start", {"agent": agent.id, "label": agent.label, "icon": agent.icon}))

    user_msg = agent.build_user(user_input)
    chunks: list[str] = []
    try:
        async for tok in client.stream(agent.system, user_msg, agent.max_tokens):
            chunks.append(tok)
            await queue.put(("token", {"agent": agent.id, "text": tok}))
    except Exception as e:
        await queue.put(("error", {"agent": agent.id, "message": str(e)}))
        return ""

    full = "".join(chunks)
    elapsed = round(time.time() - started, 2)
    await queue.put(("done", {"agent": agent.id, "elapsed_s": elapsed, "tokens_estimate": len(full) // 4}))
    return full


async def run_pipeline(user_input: dict) -> AsyncIterator[str]:
    """Run the full pipeline. Yields SSE-formatted strings."""
    client = LLMClient()
    queue: asyncio.Queue = asyncio.Queue()

    yield _sse("pipeline_start", {
        "provider": client.config.provider,
        "model": client.config.model,
        "agents": [{"id": a.id, "label": a.label, "icon": a.icon} for a in AGENTS],
    })

    # Phase 1: parallel agents
    yield _sse("phase", {"phase": "parallel_agents"})

    tasks = [asyncio.create_task(_run_agent(client, a, user_input, queue)) for a in AGENTS]

    # Drain queue while tasks run
    finished_count = 0
    target = len(AGENTS)
    pending_tasks = asyncio.gather(*tasks, return_exceptions=True)

    while finished_count < target:
        try:
            event, data = await asyncio.wait_for(queue.get(), timeout=120.0)
        except asyncio.TimeoutError:
            yield _sse("error", {"message": "agent timeout"})
            break
        yield _sse(event, data)
        if event == "done" or event == "error":
            finished_count += 1

    agent_results = await pending_tasks
    agent_outputs = {a.id: (r if isinstance(r, str) else "") for a, r in zip(AGENTS, agent_results)}

    # Phase 2: synthesizer (long-chain)
    yield _sse("phase", {"phase": "synthesizer"})
    yield _sse("start", {"agent": SYNTHESIZER.id, "label": SYNTHESIZER.label, "icon": SYNTHESIZER.icon})

    synth_user = build_synth_user(user_input, agent_outputs)
    started = time.time()
    chunks: list[str] = []
    try:
        async for tok in client.stream(SYNTHESIZER.system, synth_user, SYNTHESIZER.max_tokens):
            chunks.append(tok)
            yield _sse("token", {"agent": SYNTHESIZER.id, "text": tok})
    except Exception as e:
        yield _sse("error", {"agent": SYNTHESIZER.id, "message": str(e)})
        return

    final = "".join(chunks)
    yield _sse("done", {
        "agent": SYNTHESIZER.id,
        "elapsed_s": round(time.time() - started, 2),
        "tokens_estimate": len(final) // 4,
    })

    # Total token estimate across all stages
    total_chars = sum(len(o) for o in agent_outputs.values()) + len(final)
    yield _sse("pipeline_complete", {
        "total_tokens_estimate": total_chars // 4,
        "agents_completed": len([o for o in agent_outputs.values() if o]),
    })

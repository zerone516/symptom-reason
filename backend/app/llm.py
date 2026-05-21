"""LLM client wrapper. OpenAI-compatible interface for Mimo + Claude fallback."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import AsyncIterator

import httpx
from openai import AsyncOpenAI


@dataclass
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    provider: str  # "mimo" | "claude"


def load_config() -> LLMConfig:
    """Pick the first available provider from env. Mimo preferred."""
    mimo_key = os.getenv("MIMO_API_KEY", "").strip()
    if mimo_key and mimo_key != "your_mimo_key_here":
        return LLMConfig(
            api_key=mimo_key,
            base_url=os.getenv("MIMO_BASE_URL", "https://api.mimo.xiaomi.com/v1"),
            model=os.getenv("MIMO_MODEL", "mimo-7b-rl"),
            provider="mimo",
        )

    claude_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if claude_key:
        return LLMConfig(
            api_key=claude_key,
            base_url="https://api.anthropic.com/v1",
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            provider="claude",
        )

    # Demo mode — no key configured
    return LLMConfig(api_key="", base_url="", model="demo", provider="demo")


class LLMClient:
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or load_config()
        self._client: AsyncOpenAI | None = None
        if self.config.provider in ("mimo",):
            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=60.0,
            )

    async def stream(self, system: str, user: str, max_tokens: int = 1500) -> AsyncIterator[str]:
        """Yield text chunks from the model."""
        if self.config.provider == "demo":
            async for chunk in self._demo_stream(system, user):
                yield chunk
            return

        if self.config.provider == "mimo":
            async for chunk in self._openai_compat_stream(system, user, max_tokens):
                yield chunk
            return

        if self.config.provider == "claude":
            async for chunk in self._claude_stream(system, user, max_tokens):
                yield chunk
            return

    async def complete(self, system: str, user: str, max_tokens: int = 1500) -> str:
        """Non-streaming. Returns full text."""
        chunks: list[str] = []
        async for c in self.stream(system, user, max_tokens):
            chunks.append(c)
        return "".join(chunks)

    # ---------------- providers ----------------

    async def _openai_compat_stream(self, system: str, user: str, max_tokens: int):
        assert self._client is not None
        stream = await self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.4,
            stream=True,
        )
        async for event in stream:
            if event.choices and event.choices[0].delta.content:
                yield event.choices[0].delta.content

    async def _claude_stream(self, system: str, user: str, max_tokens: int):
        async with httpx.AsyncClient(timeout=60.0) as http:
            async with http.stream(
                "POST",
                f"{self.config.base_url}/messages",
                headers={
                    "x-api-key": self.config.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.config.model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                    "stream": True,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    import json as _json
                    payload = line[len("data: "):].strip()
                    if not payload or payload == "[DONE]":
                        continue
                    try:
                        ev = _json.loads(payload)
                    except Exception:
                        continue
                    if ev.get("type") == "content_block_delta":
                        delta = ev.get("delta", {}).get("text")
                        if delta:
                            yield delta

    async def _demo_stream(self, system: str, user: str):
        """Deterministic demo output when no API key is configured.
        Lets evaluators run the project without provisioning an LLM key."""
        import asyncio
        sample = (
            "[demo mode] Configure MIMO_API_KEY in .env to run real inference. "
            "This response is a placeholder demonstrating the streaming pipeline."
        )
        for word in sample.split():
            await asyncio.sleep(0.04)
            yield word + " "

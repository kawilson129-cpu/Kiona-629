"""OpenAI-compatible answer generation for DeRexi (optional).

When ``OPENAI_API_KEY`` is set, the ``/ask`` endpoint sends the retrieved
policy context to an OpenAI-compatible Chat Completions API and returns a
concise, plain-English rewrite of the guidance.

Any provider exposing an OpenAI-compatible ``/chat/completions`` endpoint works
via ``OPENAI_BASE_URL``. The default configuration targets the paid OpenAI
platform; the free Groq tier (no credit card; phone verification at signup)
hosts OpenAI's open-weight ``gpt-oss`` models at $0:

    OPENAI_BASE_URL=https://api.groq.com/openai/v1
    OPENAI_MODEL=gpt-oss-120b

If the key is missing or the call fails, the backend falls back to the
rule-based guidance in ``main.py`` so retrieval keeps working offline.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

INSTRUCTIONS = (
    "You are DeRexi, the internal policy-guidance assistant for Aurum Capital "
    "Bank. A bank employee asked a question about company policy. Answer in "
    "plain, concise English based ONLY on the policy excerpts provided in the "
    "user message. Do not invent facts that are not in the excerpts. If the "
    "excerpts do not contain enough information to answer the question, say so "
    "plainly. Write the answer as a short paragraph (3-5 sentences) of helpful "
    "employee guidance. The caller appends the source citation, so do not "
    "quote policy names or version numbers in your answer."
)


def generate_answer(question: str, context: list[dict]) -> str | None:
    """Return a plain-English answer for ``question`` grounded in ``context``.

    ``context`` is a list of retrieved policies, each a dict with keys
    ``title``, ``version_no`` and ``body``. Returns None when no API key is
    configured, the SDK is unavailable, or the request fails, letting callers
    fall back to rule-based guidance.
    """
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI  # deferred so the app still runs without the SDK

        source_block = "\n\n".join(
            f"POLICY: {item['title']} (v{item['version_no']})\n{item['body']}"
            for item in context
        )
        prompt = (
            f"QUESTION: {question}\n\n"
            f"POLICY LIBRARY CONTEXT:\n{source_block}"
        )
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, timeout=30)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            max_tokens=400,
            messages=[
                {"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": prompt},
            ],
        )
        text = (completion.choices[0].message.content or "").strip()
        return text or None
    except Exception:
        return None
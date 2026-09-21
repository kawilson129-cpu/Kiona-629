"""OpenAI-backed plain-English answers for DeRexi (optional).

When ``OPENAI_API_KEY`` is set, the ``/ask`` endpoint turns the retrieved
policy context into a concise, plain-English answer using the OpenAI
Responses API (https://developers.openai.com/docs/guides/migrate-to-responses).
Storage is disabled (``store=False``) so the bank's policy text is never kept
in OpenAI's systems. If the key is missing or a call fails, the backend falls
back to the rule-based guidance in ``main.py`` so retrieval keeps working.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
    ``title``, ``version_no`` and ``body``. Returns None when OpenAI is not
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
        client = OpenAI(api_key=OPENAI_API_KEY, timeout=30)
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=INSTRUCTIONS,
            input=[{"role": "user", "content": prompt}],
            store=False,
            temperature=0.2,
        )
        text = (response.output_text or "").strip()
        return text or None
    except Exception:
        return None
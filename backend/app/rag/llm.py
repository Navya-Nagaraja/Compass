"""
Thin provider abstraction so the rest of the app never imports an SDK
directly. Add a new provider by writing one function and registering it
in `_PROVIDERS` -- nothing else in the app needs to change.
"""
from __future__ import annotations

import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT = (
    "You are Compass, an internal engineering assistant. Answer the "
    "engineer's question using ONLY the provided context snippets. If the "
    "context doesn't contain the answer, say so plainly instead of "
    "guessing. Keep answers concise and cite which source each fact came "
    "from by its document name."
)


def _build_user_message(question: str, context_blocks: list[str]) -> str:
    context = "\n\n".join(context_blocks) if context_blocks else "(no matching context found)"
    return f"Context:\n{context}\n\nQuestion: {question}"


def _call_anthropic(question: str, context_blocks: list[str]) -> str:
    import anthropic

    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=1000,
        system=RAG_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_message(question, context_blocks)}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _call_openai(question: str, context_blocks: list[str]) -> str:
    from openai import OpenAI

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(question, context_blocks)},
        ],
    )
    return response.choices[0].message.content or ""


def _call_mock(question: str, context_blocks: list[str]) -> str:
    """No API key configured. Returns a deterministic, clearly-labeled
    response so the full pipeline (embed -> search -> "generate") is still
    demoable without any external dependency."""
    if not context_blocks:
        return (
            "[mock LLM] No indexed documents matched this question yet. "
            "Ingest some docs via POST /api/docs/ingest, then ask again."
        )
    preview = context_blocks[0][:280]
    return (
        f"[mock LLM -- set COMPASS_LLM_PROVIDER=anthropic or openai for real "
        f"answers] Based on the top matching chunk, here's a relevant excerpt "
        f"for '{question}':\n\n{preview}..."
    )


_PROVIDERS = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "mock": _call_mock,
}


def generate_answer(question: str, context_blocks: list[str]) -> str:
    settings = get_settings()
    provider_fn = _PROVIDERS.get(settings.llm_provider, _call_mock)
    try:
        return provider_fn(question, context_blocks)
    except Exception:
        logger.exception("LLM provider '%s' failed, falling back to mock", settings.llm_provider)
        return _call_mock(question, context_blocks)

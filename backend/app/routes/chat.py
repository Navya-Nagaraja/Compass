import time

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.rag.llm import generate_answer
from app.rag.vector_store import get_vector_store

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def ask_question(payload: ChatRequest) -> ChatResponse:
    settings = get_settings()
    store = get_vector_store()
    top_k = payload.top_k or settings.top_k

    results = store.search(payload.question, top_k)
    context_blocks = [f"[{chunk.document} #{chunk.chunk_index}] {chunk.text}" for chunk, _ in results]

    start = time.perf_counter()
    answer = generate_answer(payload.question, context_blocks)
    latency_ms = (time.perf_counter() - start) * 1000

    sources = [
        SourceChunk(document=chunk.document, chunk_index=chunk.chunk_index, score=score, text=chunk.text[:300])
        for chunk, score in results
    ]
    return ChatResponse(answer=answer, sources=sources, latency_ms=round(latency_ms, 2))

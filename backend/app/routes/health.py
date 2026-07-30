from fastapi import APIRouter

from app.core.config import get_settings
from app.models.schemas import HealthResponse
from app.rag.vector_store import get_vector_store

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    store = get_vector_store()
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        llm_provider=settings.llm_provider,
        documents_indexed=store.document_count(),
    )

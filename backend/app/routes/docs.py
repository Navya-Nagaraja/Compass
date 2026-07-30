from fastapi import APIRouter

from app.core.config import get_settings
from app.models.schemas import IngestRequest, IngestResponse
from app.rag.vector_store import get_vector_store

router = APIRouter(prefix="/api/docs", tags=["docs"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(payload: IngestRequest) -> IngestResponse:
    settings = get_settings()
    store = get_vector_store()
    chunks_indexed = store.add_document(
        document_name=payload.document_name,
        text=payload.text,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    return IngestResponse(document_name=payload.document_name, chunks_indexed=chunks_indexed)

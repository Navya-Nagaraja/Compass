from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Engineer's natural-language question")
    top_k: int | None = Field(None, ge=1, le=20)


class SourceChunk(BaseModel):
    document: str
    chunk_index: int
    score: float
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    latency_ms: float


class IngestRequest(BaseModel):
    document_name: str
    text: str


class IngestResponse(BaseModel):
    document_name: str
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str
    environment: str
    llm_provider: str
    documents_indexed: int

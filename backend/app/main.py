import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.routes import chat, docs, health

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Compass starting up | provider=%s | environment=%s", settings.llm_provider, settings.environment)
    yield
    logger.info("Compass shutting down")


app = FastAPI(
    title="Compass API",
    description="RAG-powered internal developer platform: search docs/runbooks and get grounded answers.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(docs.router)

# Exposes /metrics for Prometheus scraping (request latency, status codes,
# in-flight requests) -- same pattern used for the Assist Platform's
# inference services.
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

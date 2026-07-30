"""
Minimal but production-shaped vector store for the docs/runbook assistant.

Design notes:
- Embeddings run locally via sentence-transformers, so ingestion and search
  work with zero API keys and zero external calls (keeps the RAG loop cheap
  and demoable). Swapping this for Bedrock/OpenAI embeddings later is a
  one-function change (see `_embed`).
- FAISS holds vectors; a parallel list holds the matching text + metadata,
  since FAISS itself is vector-only storage.
- Index + metadata are persisted to disk so the container can restart
  without re-ingesting everything.
"""
from __future__ import annotations

import json
import logging
import pickle
import threading
from dataclasses import dataclass, asdict
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    document: str
    chunk_index: int
    text: str


class VectorStore:
    """Thread-safe wrapper around a FAISS flat index plus its metadata."""

    def __init__(self) -> None:
        settings = get_settings()
        self._lock = threading.Lock()
        self._path = Path(settings.vector_store_path)
        self._path.mkdir(parents=True, exist_ok=True)

        logger.info("Loading embedding model %s", settings.embedding_model)
        self._model = SentenceTransformer(settings.embedding_model)
        self._dim = self._model.get_sentence_embedding_dimension()

        self._index = faiss.IndexFlatIP(self._dim)  # cosine sim via normalized vectors
        self._chunks: list[Chunk] = []

        self._load_from_disk()

    # ---- public API -----------------------------------------------------

    def document_count(self) -> int:
        with self._lock:
            return len({c.document for c in self._chunks})

    def chunk_count(self) -> int:
        with self._lock:
            return len(self._chunks)

    def add_document(self, document_name: str, text: str, chunk_size: int, overlap: int) -> int:
        chunks = _split_into_chunks(text, chunk_size, overlap)
        vectors = self._embed(chunks)

        with self._lock:
            start_index = len(self._chunks)
            self._index.add(vectors)
            for i, chunk_text in enumerate(chunks):
                self._chunks.append(Chunk(document=document_name, chunk_index=start_index + i, text=chunk_text))
            self._save_to_disk()

        logger.info("Indexed %d chunks for document '%s'", len(chunks), document_name)
        return len(chunks)

    def search(self, query: str, top_k: int) -> list[tuple[Chunk, float]]:
        query_vector = self._embed([query])
        with self._lock:
            if len(self._chunks) == 0:
                return []
            k = min(top_k, len(self._chunks))
            scores, indices = self._index.search(query_vector, k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue
                results.append((self._chunks[idx], float(score)))
            return results

    # ---- internals --------------------------------------------------------

    def _embed(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.astype("float32")

    def _save_to_disk(self) -> None:
        faiss.write_index(self._index, str(self._path / "index.faiss"))
        with open(self._path / "chunks.pkl", "wb") as f:
            pickle.dump([asdict(c) for c in self._chunks], f)

    def _load_from_disk(self) -> None:
        index_file = self._path / "index.faiss"
        chunks_file = self._path / "chunks.pkl"
        if index_file.exists() and chunks_file.exists():
            self._index = faiss.read_index(str(index_file))
            with open(chunks_file, "rb") as f:
                self._chunks = [Chunk(**d) for d in pickle.load(f)]
            logger.info("Loaded %d existing chunks from disk", len(self._chunks))


def _split_into_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Simple sliding-window splitter on whitespace-normalized text.
    Good enough for markdown/API-spec docs; swap for a semantic/markdown-aware
    splitter if ingesting long-form prose."""
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
    return chunks


_store: VectorStore | None = None
_store_lock = threading.Lock()


def get_vector_store() -> VectorStore:
    """Lazily-constructed singleton so the (slow-ish) embedding model loads
    once per process, not once per request."""
    global _store
    if _store is None:
        with _store_lock:
            if _store is None:
                _store = VectorStore()
    return _store

# Compass

An AI-powered internal developer platform: engineers ask questions in
plain English and get answers grounded in your team's own docs, API
specs, and runbooks — with the source chunks and similarity scores
shown alongside every answer.

Compass is a small, self-contained version of the kind of platform
tooling used at companies like Mastercard, ASU, and Oracle: a
retrieval-augmented generation (RAG) service, a React dashboard, CI/CD,
containerized deployment, and Prometheus/Grafana monitoring, all wired
together in one repo.

## Overview

Compass is a full-stack AI developer platform that lets engineering
teams query their own documentation, API specs, and runbooks in
natural language instead of searching manually. It combines a
retrieval-augmented generation (RAG) pipeline — local embeddings, FAISS
vector search, and a swappable LLM layer (Anthropic/OpenAI) — with a
React dashboard, containerized deployment, CI/CD via GitHub Actions,
and Prometheus/Grafana monitoring. It runs fully out of the box with
zero API keys in "mock mode," so anyone can clone it and see the
entire pipeline working end to end.

## Why this exists

Most "AI chatbot" demos either hardcode a single document or require an
API key just to click around. Compass is built to run **with zero API
keys** in mock mode, so anyone can clone it, `docker compose up`, and
see the full ingest → embed → retrieve → answer loop working end to
end. Point it at a real Anthropic or OpenAI key and it becomes a real
assistant over your own docs.

## Architecture

```
Engineer → React dashboard → FastAPI backend → RAG engine (embeddings + FAISS) → LLM (Anthropic / OpenAI / mock)
                                     ↑                                                    |
                              GitHub Actions CI/CD                              Prometheus + Grafana
```

- **Frontend** — React + Vite, no UI framework dependency. A
  terminal-style console: ask a question, watch the answer stream in,
  see the retrieved source chunks and their similarity scores in the
  side panel.
- **Backend** — FastAPI. Ingests text into chunks, embeds them locally
  with `sentence-transformers` (no API key needed for retrieval),
  stores vectors in FAISS, and calls an LLM provider to generate the
  final answer grounded in the retrieved context.
- **LLM provider layer** — one function per provider
  (`app/rag/llm.py`). Defaults to a `mock` provider that still runs the
  full retrieval pipeline, so the app is demoable with nothing configured.
- **Infra** — Dockerfiles for both services, a `docker-compose.yml` for
  local dev, Kubernetes manifests for a real cluster, a GitHub Actions
  pipeline that tests, builds, and pushes images, and a Prometheus
  config that scrapes the backend's `/metrics` endpoint out of the box.

## Quickstart (no API key required)

```bash
git clone <your-fork-url>
cd compass
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (login `admin` / `admin`)

Index a doc from the sidebar, ask a question, and watch the sources
panel populate with the chunks Compass used to answer.

### Using a real LLM

Copy `.env.example` to `.env`, set `COMPASS_LLM_PROVIDER=anthropic` (or
`openai`) and add your API key, then re-run `docker compose up --build`.

## Running locally without Docker

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Tests**
```bash
cd backend
pytest -v
```

## Project layout

```
compass/
├── backend/            FastAPI service, RAG pipeline, tests
├── frontend/            React dashboard (Vite)
├── k8s/                 Kubernetes manifests (deployments, services, config)
├── monitoring/           Prometheus scrape config
├── .github/workflows/    CI/CD pipeline
└── docker-compose.yml    One-command local stack
```

## What this demonstrates

- Full-stack ownership: React/TypeScript-style frontend patterns, a
  typed FastAPI backend, and the infrastructure that ships them.
- RAG from scratch: chunking, local embeddings, vector search, and a
  swappable LLM layer — not just a call to an API.
- Production habits: health checks, structured logging, Prometheus
  metrics, readiness/liveness probes, and a CI pipeline that actually
  gates on tests before building images.



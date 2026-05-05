# DClaw Research

Deep Research Agent — local-first multi-hop research with knowledge graphs and publication-ready reports.

## Features

- **Research Plan Editor** — Edit, add, remove, and reorder search queries before execution
- **Knowledge Graph View** — Interactive React Flow visualization of entities, claims, and sources
- **Local Synthesis** — Ollama (Qwen 32B, nomic-embed-text) with OpenRouter fallback
- **Source Verification** — Cross-reference claims across sources; flag contradictions
- **Report Templates** — Academic, Business Brief, Investment Memo, Product Comparison
- **Research Memory** — Queryable library of past projects

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Ollama (for local LLM) or OpenRouter API key
- Firecrawl API key or SearXNG instance

### Run with Docker Compose

```bash
cd dclaw-research
docker compose -f docker-compose.dev.yml up --build
```

- Backend: http://localhost:8095
- Frontend: http://localhost:3003

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL |
| `REDIS_URL` | Redis URL for Celery |
| `OLLAMA_BASE_URL` | Ollama host |
| `FIRECRAWL_API_KEY` | Firecrawl API key |
| `SEARXNG_URL` | Local SearXNG URL (fallback) |
| `OPENROUTER_API_KEY` | OpenRouter fallback key |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/research` | Create project + generate plan |
| GET | `/api/v1/research/{id}/plan` | Get editable plan |
| POST | `/api/v1/research/{id}/execute` | Start Celery job |
| GET | `/api/v1/research/{id}/status` | Progress polling |
| GET | `/api/v1/research/{id}/sources` | Paginated sources |
| GET | `/api/v1/research/{id}/graph` | Knowledge graph |
| GET | `/api/v1/research/{id}/report` | Final report |
| PUT | `/api/v1/research/{id}/report` | Save edits |
| WS | `/api/v1/research/{id}/progress` | Live updates |

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy+asyncpg, Celery, NetworkX, hatchling
- **Frontend**: Next.js 14, Tailwind, shadcn/ui, React Flow, TipTap
- **Desktop**: Tauri v2
- **Search**: Firecrawl, SearXNG, Jina AI
- **AI**: Ollama (Qwen 32B), OpenRouter fallback
- **Vector DB**: pgvector

## License

MIT

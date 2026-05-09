# DClaw Research — v1.2 Feature Roadmap

> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (paper-qa, gpt-researcher), AI product research (Elicit, Consensus, Perplexity, Scite)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Research project CRUD
- [ ] Source/document management
- [ ] Note-taking & annotation
- [ ] Basic report generation
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI Research Copilot (Scientist Agent)
**Description:** AI research assistant that searches literature, synthesizes findings, and generates reports with citations. "What's the latest on CRISPR gene editing for sickle cell?"
- **AI Angle:** Multi-source RAG + web search + academic API integration. Structured report generation.
- **Backend:** `/api/v1/ai/research-chat` endpoint. Research orchestration pipeline.
- **Frontend:** Research chat with citation cards. Report preview.
- **Files:** `backend/app/services/research_ai.py`, `frontend/src/components/research-copilot.tsx`

#### 2. Automated Literature Review
**Description:** Upload topic or question. AI searches PubMed, arXiv, Semantic Scholar, and synthesizes a literature review.
- **AI Angle:** Search + filtering + synthesis + citation formatting.
- **Backend:** Literature search orchestrator. PDF fetcher.
- **Frontend:** Review generation wizard. Editable outline.
- **Files:** `backend/app/services/lit_review.py`

#### 3. Source Management & Annotation
**Description:** Import papers, web pages, and datasets. Highlight, annotate, and tag sources.
- **Backend:** Source ingestion with metadata extraction. Annotation store.
- **Frontend:** PDF viewer with annotation layer. Source library with filters.
- **Files:** `backend/app/services/sources.py`

#### 4. Citation & Reference Management
**Description:** Auto-generate citations in APA, MLA, Chicago, BibTeX. Citation graph visualization.
- **Backend:** Citation formatter. Citation network analysis.
- **Frontend:** Citation manager. Graph view of cited works.
- **Files:** `backend/app/services/citations.py`

### P1 — Should Have (v1.1–1.2)

#### 5. Research Report Generator
**Description:** Generate structured research reports with executive summary, methodology, findings, and recommendations.
- **AI Angle:** LLM report generation with section templates.
- **Backend:** Report template engine. Section generation pipeline.
- **Frontend:** Report editor with AI-generate sections.

#### 6. Data Extraction from Papers
**Description:** Extract tables, figures, and key data points from PDFs into structured format.
- **AI Angle:** Table extraction + figure caption analysis.
- **Backend:** PDF parsing pipeline with structured output.
- **Frontend:** Extracted data table with source link.

#### 7. Collaboration & Peer Review
**Description:** Share research projects. Comment, suggest edits, track versions.
- **Backend:** Collaboration permissions. Comment threading.
- **Frontend:** Shared workspace with activity feed.

#### 8. Trend & Gap Analysis
**Description:** Identify research trends, emerging topics, and knowledge gaps in a field.
- **AI Angle:** Topic modeling + trend detection on literature corpus.
- **Backend:** Trend analysis engine.
- **Frontend:** Trend dashboard with gap heatmap.

### P2 — Could Have (v1.3+)

#### 9. AI Hypothesis Generation
**Description:** AI suggests testable hypotheses based on observed patterns in literature.

#### 10. Experiment Design Assistant
**Description:** AI suggests experimental design, controls, and sample size calculations.

#### 11. Peer Review Simulator
**Description:** AI simulates peer review feedback on drafts before submission.

#### 12. Research Impact Prediction
**Description:** AI predicts citation potential and impact factor of papers.

---

## Implementation Priority

1. **Week 1–2:** AI Research Copilot (P0.1) + Literature Review (P0.2)
2. **Week 3–4:** Source Management (P0.3) + Citations (P0.4)
3. **Week 5–6:** Report Generator (P1.5) + Data Extraction (P1.6)
4. **Week 7–8:** Collaboration (P1.7) + Trend Analysis (P1.8)

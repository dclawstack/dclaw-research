"""Celery tasks for the research pipeline."""

import asyncio
from datetime import datetime
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import sync_engine
from app.models.research import (
    ResearchProject,
    SearchQuery,
    Source,
    Claim,
    ReportSection,
)
from app.services.search_service import run_search, scrape_url, _credibility_heuristic
from app.services.synthesis_service import (
    generate_research_plan,
    summarize_source,
    generate_report,
    generate_sections_from_markdown,
)
from app.services.graph_builder import build_graph_from_project
from app.services.verification_service import verify_claims_against_sources


def _notify(project_id: str, status: str, message: str, percent: int) -> None:
    """Store progress in Redis for WebSocket polling."""
    from app.core.redis import set_progress
    payload = {
        "project_id": project_id,
        "status": status,
        "message": message,
        "percent": percent,
        "timestamp": datetime.now().isoformat(),
    }
    set_progress(project_id, payload)


class SQLAlchemyTask(Task):
    """Base Celery task with a sync DB session."""

    _db: Session | None = None

    @property
    def db(self) -> Session:
        if self._db is None:
            from sqlalchemy.orm import sessionmaker
            SessionLocal = sessionmaker(bind=sync_engine)
            self._db = SessionLocal()
        return self._db


@celery_app.task(bind=True, base=SQLAlchemyTask)
def execute_research(self, project_id: str) -> dict:
    """Main research pipeline."""
    db = self.db
    project = db.query(ResearchProject).filter(
        ResearchProject.id == UUID(project_id)
    ).first()
    if not project:
        return {"error": "Project not found"}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Phase 1: Planning (if not already done)
        _notify(project_id, "planning", "Generating research plan...", 5)
        queries = db.query(SearchQuery).filter(
            SearchQuery.project_id == UUID(project_id)
        ).order_by(SearchQuery.sort_order).all()

        if not queries:
            plan_queries = loop.run_until_complete(generate_research_plan(project.query))
            for i, q in enumerate(plan_queries):
                db.add(
                    SearchQuery(
                        project_id=UUID(project_id),
                        query_text=q,
                        sort_order=i,
                    )
                )
            db.commit()
            queries = db.query(SearchQuery).filter(
                SearchQuery.project_id == UUID(project_id)
            ).order_by(SearchQuery.sort_order).all()

        # Phase 2: Searching
        total = len(queries)
        all_search_results = []
        for i, sq in enumerate(queries):
            _notify(
                project_id,
                "searching",
                f"Searching: {sq.query_text}",
                10 + int(40 * (i / total)),
            )
            sq.status = "running"
            db.commit()
            results = loop.run_until_complete(run_search(sq.query_text))
            sq.status = "done"
            sq.results_count = len(results)
            sq.executed_at = datetime.now()
            db.commit()
            all_search_results.extend(results)

        # Phase 3: Scraping
        unique_urls = {r["url"] for r in all_search_results if r.get("url")}
        scraped = []
        total_urls = len(unique_urls)
        for i, url in enumerate(unique_urls):
            _notify(
                project_id,
                "searching",
                f"Scraping: {url}",
                50 + int(20 * (i / total_urls)),
            )
            data = loop.run_until_complete(scrape_url(url))
            if len(data.get("text", "")) > 200:
                source = Source(
                    project_id=UUID(project_id),
                    url=data["url"],
                    title=data.get("title", ""),
                    author=data.get("author", ""),
                    publish_date=data.get("date"),
                    full_text=data.get("text", ""),
                    domain=data["url"].split("/")[2] if "//" in data["url"] else "",
                    credibility_score=_credibility_heuristic(
                        data["url"], data.get("date")
                    ),
                )
                db.add(source)
                scraped.append(source)
        db.commit()

        # Phase 4: Synthesis (summaries + claims)
        _notify(project_id, "synthesizing", "Synthesizing sources...", 70)
        for source in scraped:
            summary_data = loop.run_until_complete(
                summarize_source(source.full_text, source.url)
            )
            for claim_text in summary_data.get("claims", []):
                entities = []
                # Simple entity extraction placeholder
                db.add(
                    Claim(
                        source_id=source.id,
                        project_id=UUID(project_id),
                        claim_text=claim_text,
                        entity_mentions=entities,
                        confidence=source.credibility_score,
                    )
                )
        db.commit()

        sources = db.query(Source).filter(
            Source.project_id == UUID(project_id)
        ).all()
        claims = db.query(Claim).filter(
            Claim.project_id == UUID(project_id)
        ).all()

        # Phase 5: Verification
        _notify(project_id, "synthesizing", "Verifying claims...", 80)
        loop.run_until_complete(
            verify_claims_against_sources(db, UUID(project_id), sources)
        )

        # Phase 6: Knowledge Graph
        _notify(project_id, "synthesizing", "Building knowledge graph...", 85)
        loop.run_until_complete(
            build_graph_from_project(db, UUID(project_id), sources, claims)
        )

        # Phase 7: Report Writing
        _notify(project_id, "writing", "Writing report...", 90)
        report_md = loop.run_until_complete(generate_report(project, sources, claims))
        project.report_markdown = report_md

        # Parse sections
        sections = loop.run_until_complete(
            generate_sections_from_markdown(UUID(project_id), report_md)
        )
        for sec in sections:
            db.add(ReportSection(**sec))

        project.status = "done"
        db.commit()
        _notify(project_id, "done", "Research complete.", 100)
        return {"status": "done", "project_id": project_id}

    except Exception as exc:
        project.status = "error"
        db.commit()
        _notify(project_id, "error", str(exc), 0)
        raise

    finally:
        loop.close()

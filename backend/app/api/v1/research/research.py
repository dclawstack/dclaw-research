"""Research project endpoints."""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.celery_app import celery_app
from app.models.research import ResearchProject, SearchQuery
from app.schemas.research import (
    ResearchProjectCreate,
    ResearchProjectOut,
    ResearchPlanOut,
    SearchQueryCreate,
    SearchQueryOut,
    ProgressUpdate,
)
from app.services.synthesis_service import generate_research_plan
from app.services.research_tasks import execute_research

router = APIRouter()


@router.post("/", response_model=ResearchProjectOut, status_code=201)
async def create_research(
    payload: ResearchProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> ResearchProject:
    """Create a new research project and generate a plan."""
    project = ResearchProject(
        title=payload.query[:200],
        query=payload.query,
        template_type=payload.template_type,
        status="planning",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Generate plan asynchronously
    plan_queries = await generate_research_plan(payload.query)
    for i, q in enumerate(plan_queries):
        db.add(
            SearchQuery(
                project_id=project.id,
                query_text=q,
                sort_order=i,
            )
        )
    await db.commit()
    return project


@router.get("/{project_id}/plan", response_model=ResearchPlanOut)
async def get_plan(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the editable research plan."""
    project = await db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(SearchQuery)
        .where(SearchQuery.project_id == project_id)
        .order_by(SearchQuery.sort_order)
    )
    queries = result.scalars().all()
    return {"project": project, "queries": queries}


@router.put("/{project_id}/plan")
async def update_plan(
    project_id: UUID,
    queries: list[SearchQueryCreate],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Replace the research plan queries."""
    project = await db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from sqlalchemy import delete
    await db.execute(delete(SearchQuery).where(SearchQuery.project_id == project_id))

    for i, q in enumerate(queries):
        db.add(
            SearchQuery(
                project_id=project_id,
                query_text=q.query_text,
                sort_order=i,
            )
        )
    await db.commit()
    return {"status": "updated"}


@router.post("/{project_id}/execute")
async def execute_plan(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Start the Celery research job."""
    project = await db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status not in ("planning", "error"):
        raise HTTPException(status_code=400, detail="Research already in progress or done")

    project.status = "searching"
    await db.commit()

    task = execute_research.delay(str(project_id))
    return {"task_id": task.id, "status": "started"}


@router.get("/{project_id}/status")
async def get_status(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get current research status."""
    project = await db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from app.core.redis import get_progress
    progress = get_progress(str(project_id))
    return {
        "project_id": str(project_id),
        "status": project.status,
        "progress": progress,
    }


@router.websocket("/{project_id}/progress")
async def websocket_progress(websocket: WebSocket, project_id: UUID):
    """Stream live progress updates."""
    await websocket.accept()
    from app.core.redis import get_progress
    try:
        while True:
            progress = get_progress(str(project_id)) or {}
            await websocket.send_json(progress)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass


@router.get("/", response_model=list[ResearchProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> list[ResearchProject]:
    """List all research projects."""
    from sqlalchemy import select
    result = await db.execute(
        select(ResearchProject)
        .order_by(ResearchProject.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

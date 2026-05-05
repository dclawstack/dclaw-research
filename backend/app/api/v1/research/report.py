"""Report endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.research import ResearchProject, ReportSection
from app.schemas.research import ReportOut, ReportSectionOut

router = APIRouter()


@router.get("/{project_id}/report", response_model=ReportOut)
async def get_report(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the final report."""
    project = await db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(ReportSection)
        .where(ReportSection.project_id == project_id)
        .order_by(ReportSection.sort_order)
    )
    sections = result.scalars().all()

    return {
        "project_id": project.id,
        "title": project.title,
        "template_type": project.template_type,
        "markdown": project.report_markdown,
        "sections": sections,
        "created_at": project.created_at,
    }


@router.put("/{project_id}/report")
async def update_report(
    project_id: UUID,
    sections: list[ReportSectionOut],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Save user edits to the report sections."""
    project = await db.get(ResearchProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from sqlalchemy import delete
    await db.execute(delete(ReportSection).where(ReportSection.project_id == project_id))

    full_md_parts = []
    for i, sec in enumerate(sections):
        db.add(
            ReportSection(
                project_id=project_id,
                heading=sec.heading,
                content_markdown=sec.content_markdown,
                citations=sec.citations,
                sort_order=i,
            )
        )
        full_md_parts.append(f"## {sec.heading}\n\n{sec.content_markdown}\n")

    project.report_markdown = "\n".join(full_md_parts)
    await db.commit()
    return {"status": "saved"}


@router.post("/{project_id}/verify")
async def verify_report(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Re-run claim verification."""
    from app.services.research_tasks import execute_research
    task = execute_research.delay(str(project_id))
    return {"task_id": task.id, "status": "verification_started"}

"""Source endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.research import Source
from app.schemas.research import SourceOut

router = APIRouter()


@router.get("/{project_id}/sources", response_model=list[SourceOut])
async def list_sources(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> list[Source]:
    """List sources for a project."""
    result = await db.execute(
        select(Source)
        .where(Source.project_id == project_id)
        .order_by(Source.credibility_score.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

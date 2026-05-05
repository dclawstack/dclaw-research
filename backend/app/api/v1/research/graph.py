"""Knowledge graph endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.research import KnowledgeGraphNode, KnowledgeGraphEdge
from app.schemas.research import GraphOut, GraphNodeOut, GraphEdgeOut

router = APIRouter()


@router.get("/{project_id}/graph", response_model=GraphOut)
async def get_graph(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get knowledge graph nodes and edges for a project."""
    nodes_result = await db.execute(
        select(KnowledgeGraphNode).where(KnowledgeGraphNode.project_id == project_id)
    )
    nodes = nodes_result.scalars().all()

    edges_result = await db.execute(
        select(KnowledgeGraphEdge).where(KnowledgeGraphEdge.project_id == project_id)
    )
    edges = edges_result.scalars().all()

    return {"nodes": nodes, "edges": edges}

"""Pydantic schemas for research domain."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SearchQueryCreate(BaseModel):
    query_text: str
    sort_order: int = 0


class SearchQueryOut(BaseModel):
    id: UUID
    query_text: str
    status: str
    results_count: int
    executed_at: datetime | None
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SourceOut(BaseModel):
    id: UUID
    url: str
    title: str
    author: str
    publish_date: datetime | None
    credibility_score: float
    domain: str
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimOut(BaseModel):
    id: UUID
    source_id: UUID
    claim_text: str
    entity_mentions: list[str]
    verified_against_sources: list[UUID]
    contradiction_flags: list[Any]
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GraphNodeOut(BaseModel):
    id: UUID
    label: str
    node_type: str
    meta: dict[str, Any]
    x: float | None
    y: float | None

    model_config = ConfigDict(from_attributes=True)


class GraphEdgeOut(BaseModel):
    id: UUID
    source_node_id: UUID
    target_node_id: UUID
    relation_type: str
    strength: float
    meta: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class GraphOut(BaseModel):
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]


class ReportSectionOut(BaseModel):
    id: UUID
    heading: str
    content_markdown: str
    citations: list[UUID]
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class ReportOut(BaseModel):
    project_id: UUID
    title: str
    template_type: str
    markdown: str
    sections: list[ReportSectionOut]
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ResearchProjectCreate(BaseModel):
    query: str
    template_type: str = "academic"


class ResearchProjectOut(BaseModel):
    id: UUID
    title: str
    query: str
    status: str
    template_type: str
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ResearchPlanOut(BaseModel):
    project: ResearchProjectOut
    queries: list[SearchQueryOut]


class ProgressUpdate(BaseModel):
    project_id: UUID
    status: str
    message: str
    percent: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

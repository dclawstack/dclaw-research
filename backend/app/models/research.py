"""Research domain models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class ResearchProject(Base):
    """A research project initiated by the user."""

    __tablename__ = "research_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    query = Column(Text, nullable=False)
    plan_json = Column(JSON, default=dict)
    status = Column(
        String(50), default="planning", nullable=False
    )  # planning|searching|synthesizing|writing|done|error
    report_markdown = Column(Text, default="")
    template_type = Column(String(50), default="academic", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    search_queries = relationship(
        "SearchQuery", back_populates="project", cascade="all, delete-orphan"
    )
    sources = relationship(
        "Source", back_populates="project", cascade="all, delete-orphan"
    )
    claims = relationship(
        "Claim", back_populates="project", cascade="all, delete-orphan"
    )
    graph_nodes = relationship(
        "KnowledgeGraphNode", back_populates="project", cascade="all, delete-orphan"
    )
    graph_edges = relationship(
        "KnowledgeGraphEdge", back_populates="project", cascade="all, delete-orphan"
    )
    report_sections = relationship(
        "ReportSection", back_populates="project", cascade="all, delete-orphan"
    )


class SearchQuery(Base):
    """A planned or executed search query."""

    __tablename__ = "search_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False
    )
    query_text = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    results_count = Column(Integer, default=0)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("ResearchProject", back_populates="search_queries")


class Source(Base):
    """A scraped source document."""

    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False
    )
    url = Column(Text, nullable=False)
    title = Column(String(1000), default="")
    author = Column(String(500), default="")
    publish_date = Column(DateTime(timezone=True), nullable=True)
    full_text = Column(Text, default="")
    credibility_score = Column(Float, default=0.0)
    domain = Column(String(500), default="")
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    embedding_id = Column(String(100), nullable=True)

    project = relationship("ResearchProject", back_populates="sources")
    claims = relationship("Claim", back_populates="source", cascade="all, delete-orphan")


class Claim(Base):
    """An extracted claim from a source."""

    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False
    )
    claim_text = Column(Text, nullable=False)
    entity_mentions = Column(ARRAY(String), default=list)
    verified_against_sources = Column(ARRAY(UUID(as_uuid=True)), default=list)
    contradiction_flags = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source = relationship("Source", back_populates="claims")
    project = relationship("ResearchProject", back_populates="claims")


class KnowledgeGraphNode(Base):
    """A node in the knowledge graph."""

    __tablename__ = "knowledge_graph_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False
    )
    label = Column(String(500), nullable=False)
    node_type = Column(String(50), nullable=False)  # entity|claim|source
    meta = Column(JSON, default=dict)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)

    project = relationship("ResearchProject", back_populates="graph_nodes")
    outgoing_edges = relationship(
        "KnowledgeGraphEdge",
        foreign_keys="KnowledgeGraphEdge.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    incoming_edges = relationship(
        "KnowledgeGraphEdge",
        foreign_keys="KnowledgeGraphEdge.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )


class KnowledgeGraphEdge(Base):
    """An edge in the knowledge graph."""

    __tablename__ = "knowledge_graph_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False
    )
    source_node_id = Column(
        UUID(as_uuid=True), ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id = Column(
        UUID(as_uuid=True), ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
    relation_type = Column(String(100), nullable=False)
    strength = Column(Float, default=1.0)
    meta = Column(JSON, default=dict)

    project = relationship("ResearchProject", back_populates="graph_edges")
    source_node = relationship(
        "KnowledgeGraphNode", foreign_keys=[source_node_id], back_populates="outgoing_edges"
    )
    target_node = relationship(
        "KnowledgeGraphNode", foreign_keys=[target_node_id], back_populates="incoming_edges"
    )


class ReportSection(Base):
    """A section of the final report."""

    __tablename__ = "report_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False
    )
    heading = Column(String(500), nullable=False)
    content_markdown = Column(Text, default="")
    citations = Column(ARRAY(UUID(as_uuid=True)), default=list)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("ResearchProject", back_populates="report_sections")

"""Knowledge graph construction from sources and claims."""

import re
from typing import Any
from uuid import UUID, uuid4

import networkx as nx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.research import (
    KnowledgeGraphNode,
    KnowledgeGraphEdge,
    Source,
    Claim,
)
from app.services.synthesis_service import generate_text


def _extract_entities(text: str) -> list[str]:
    """Simple regex-based entity extraction."""
    # Capitalized phrases of 1-3 words
    matches = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})\b", text)
    # Deduplicate preserving order
    seen = set()
    entities = []
    for m in matches:
        key = m.lower()
        if key not in seen and len(key) > 3:
            seen.add(key)
            entities.append(m)
    return entities[:20]


async def build_graph_from_project(
    db: Session, project_id: UUID, sources: list[Source], claims: list[Claim]
) -> nx.DiGraph:
    """Build a NetworkX graph and persist nodes/edges to the database."""
    G = nx.DiGraph()
    node_map: dict[str, UUID] = {}

    # Clear old graph data
    db.query(KnowledgeGraphEdge).filter(
        KnowledgeGraphEdge.project_id == project_id
    ).delete(synchronize_session=False)
    db.query(KnowledgeGraphNode).filter(
        KnowledgeGraphNode.project_id == project_id
    ).delete(synchronize_session=False)

    # Add source nodes
    for source in sources:
        node_id = uuid4()
        node_map[f"source:{source.id}"] = node_id
        G.add_node(node_id, label=source.title or source.url, node_type="source")
        db.add(
            KnowledgeGraphNode(
                id=node_id,
                project_id=project_id,
                label=source.title or source.url,
                node_type="source",
                meta={"url": source.url, "credibility": source.credibility_score},
            )
        )

    # Add claim nodes and link to sources
    for claim in claims:
        node_id = uuid4()
        node_map[f"claim:{claim.id}"] = node_id
        G.add_node(node_id, label=claim.claim_text[:80], node_type="claim")
        db.add(
            KnowledgeGraphNode(
                id=node_id,
                project_id=project_id,
                label=claim.claim_text[:80],
                node_type="claim",
                meta={"confidence": claim.confidence},
            )
        )
        source_node_id = node_map.get(f"source:{claim.source_id}")
        if source_node_id:
            edge_id = uuid4()
            G.add_edge(source_node_id, node_id, relation="supports", strength=claim.confidence)
            db.add(
                KnowledgeGraphEdge(
                    id=edge_id,
                    project_id=project_id,
                    source_node_id=source_node_id,
                    target_node_id=node_id,
                    relation_type="supports",
                    strength=claim.confidence,
                )
            )

    # Extract entities from claims and link
    entity_nodes: dict[str, UUID] = {}
    for claim in claims:
        claim_node_id = node_map.get(f"claim:{claim.id}")
        if not claim_node_id:
            continue
        entities = claim.entity_mentions or _extract_entities(claim.claim_text)
        for ent in entities:
            if ent.lower() not in entity_nodes:
                ent_id = uuid4()
                entity_nodes[ent.lower()] = ent_id
                G.add_node(ent_id, label=ent, node_type="entity")
                db.add(
                    KnowledgeGraphNode(
                        id=ent_id,
                        project_id=project_id,
                        label=ent,
                        node_type="entity",
                        meta={},
                    )
                )
            ent_id = entity_nodes[ent.lower()]
            edge_id = uuid4()
            G.add_edge(claim_node_id, ent_id, relation="mentions", strength=1.0)
            db.add(
                KnowledgeGraphEdge(
                    id=edge_id,
                    project_id=project_id,
                    source_node_id=claim_node_id,
                    target_node_id=ent_id,
                    relation_type="mentions",
                    strength=1.0,
                )
            )

    # Cross-reference claims: link verified claims
    for claim in claims:
        if claim.verified_against_sources:
            claim_node_id = node_map.get(f"claim:{claim.id}")
            if not claim_node_id:
                continue
            for other_source_id in claim.verified_against_sources:
                other_source_node = node_map.get(f"source:{other_source_id}")
                if other_source_node and other_source_node != claim_node_id:
                    edge_id = uuid4()
                    G.add_edge(
                        other_source_node,
                        claim_node_id,
                        relation="verifies",
                        strength=0.9,
                    )
                    db.add(
                        KnowledgeGraphEdge(
                            id=edge_id,
                            project_id=project_id,
                            source_node_id=other_source_node,
                            target_node_id=claim_node_id,
                            relation_type="verifies",
                            strength=0.9,
                        )
                    )

    # Assign layout positions using spring layout
    pos = nx.spring_layout(G, seed=42)
    for node_id, (x, y) in pos.items():
        db_node = db.query(KnowledgeGraphNode).filter(
            KnowledgeGraphNode.id == node_id,
            KnowledgeGraphNode.project_id == project_id,
        ).first()
        if db_node:
            db_node.x = float(x)
            db_node.y = float(y)

    db.commit()
    return G

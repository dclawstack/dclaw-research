"use client";

import { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
} from "reactflow";
import "reactflow/dist/style.css";
import { GraphNode, GraphEdge } from "@/lib/api";

const typeColors: Record<string, string> = {
  entity: "#3b82f6",
  claim: "#f59e0b",
  source: "#10b981",
};

export default function KnowledgeGraph({
  nodes,
  edges,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
}) {
  const flowNodes: Node[] = useMemo(
    () =>
      nodes.map((n) => ({
        id: n.id,
        position: {
          x: (n.x ?? Math.random() * 800) * 300,
          y: (n.y ?? Math.random() * 800) * 300,
        },
        data: { label: n.label },
        style: {
          background: typeColors[n.node_type] || "#64748b",
          color: "#fff",
          borderRadius: 6,
          padding: 8,
          fontSize: 12,
          width: 160,
        },
      })),
    [nodes]
  );

  const flowEdges: Edge[] = useMemo(
    () =>
      edges.map((e) => ({
        id: e.id,
        source: e.source_node_id,
        target: e.target_node_id,
        label: e.relation_type,
        style: { stroke: "#94a3b8", strokeWidth: 1 + e.strength },
      })),
    [edges]
  );

  return (
    <ReactFlow
      nodes={flowNodes}
      edges={flowEdges}
      fitView
      attributionPosition="bottom-left"
    >
      <Background />
      <Controls />
      <MiniMap nodeStrokeWidth={3} />
    </ReactFlow>
  );
}

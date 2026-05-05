"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import { api, GraphNode, GraphEdge } from "@/lib/api";

const KnowledgeGraph = dynamic(
  () => import("@/components/graph/knowledge-graph"),
  { ssr: false }
);

export default function GraphPage() {
  const { id } = useParams<{ id: string }>();
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    api<{ nodes: GraphNode[]; edges: GraphEdge[] }>(`/research/${id}/graph`)
      .then((data) => {
        setNodes(data.nodes);
        setEdges(data.edges);
      })
      .catch(console.error);
  }, [id]);

  const filteredNodes =
    filter === "all" ? nodes : nodes.filter((n) => n.node_type === filter);
  const nodeIds = new Set(filteredNodes.map((n) => n.id));
  const filteredEdges = edges.filter(
    (e) => nodeIds.has(e.source_node_id) && nodeIds.has(e.target_node_id)
  );

  return (
    <div className="h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Knowledge Graph</h1>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="rounded-md border px-3 py-1 text-sm"
        >
          <option value="all">All</option>
          <option value="entity">Entities</option>
          <option value="claim">Claims</option>
          <option value="source">Sources</option>
        </select>
      </div>
      <div className="rounded-lg border h-full">
        <KnowledgeGraph nodes={filteredNodes} edges={filteredEdges} />
      </div>
    </div>
  );
}

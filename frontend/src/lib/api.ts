const API_BASE = "/api/v1";

export async function api<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json() as Promise<T>;
}

export type Project = {
  id: string;
  title: string;
  query: string;
  status: string;
  template_type: string;
  created_at: string;
  updated_at: string | null;
};

export type SearchQuery = {
  id: string;
  query_text: string;
  status: string;
  results_count: number;
  executed_at: string | null;
  sort_order: number;
};

export type Source = {
  id: string;
  url: string;
  title: string;
  author: string;
  publish_date: string | null;
  credibility_score: number;
  domain: string;
};

export type GraphNode = {
  id: string;
  label: string;
  node_type: string;
  meta: any;
  x: number | null;
  y: number | null;
};

export type GraphEdge = {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: string;
  strength: number;
};

export type ReportSection = {
  id: string;
  heading: string;
  content_markdown: string;
  citations: string[];
  sort_order: number;
};

// ── Generic typed fetch ──
// Pages reference `api<T>(path, opts)` directly. Alias of fetchJson.
export const api = fetchJson;

// ── Type stubs ──
// Permissive `any` stubs until each domain shape is locked in.
// Tighten these to real interfaces as the app stabilizes.
export type GraphEdge = any;
export type GraphNode = any;
export type Project = any;
export type ReportSection = any;
export type SearchQuery = any;
export type Source = any;

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, Project, SearchQuery } from "@/lib/api";

export default function PlanPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [queries, setQueries] = useState<SearchQuery[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api<{ project: Project; queries: SearchQuery[] }>(`/research/${id}/plan`)
      .then((data) => {
        setProject(data.project);
        setQueries(data.queries);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  function updateQuery(index: number, text: string) {
    const next = [...queries];
    next[index] = { ...next[index], query_text: text };
    setQueries(next);
  }

  function addQuery() {
    setQueries([
      ...queries,
      {
        id: "new-" + Date.now(),
        query_text: "",
        status: "pending",
        results_count: 0,
        executed_at: null,
        sort_order: queries.length,
      },
    ]);
  }

  function removeQuery(index: number) {
    setQueries(queries.filter((_, i) => i !== index));
  }

  async function saveAndRun() {
    setSaving(true);
    try {
      await api(`/research/${id}/plan`, {
        method: "PUT",
        body: JSON.stringify(
          queries.map((q, i) => ({ query_text: q.query_text, sort_order: i }))
        ),
      });
      await api(`/research/${id}/execute`, { method: "POST" });
      router.push(`/research/${id}/live`);
    } catch (err) {
      alert("Error: " + (err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-muted-foreground">Loading plan...</p>;
  if (!project) return <p className="text-muted-foreground">Project not found.</p>;

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-1">Research Plan</h1>
      <p className="text-muted-foreground mb-6">{project.query}</p>

      <div className="space-y-3 mb-6">
        {queries.map((q, i) => (
          <div key={q.id} className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground w-6">{i + 1}</span>
            <input
              value={q.query_text}
              onChange={(e) => updateQuery(i, e.target.value)}
              className="flex-1 rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button
              onClick={() => removeQuery(i)}
              className="text-sm text-destructive hover:underline"
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <button
          onClick={addQuery}
          className="rounded-md border px-4 py-2 text-sm font-medium hover:bg-muted"
        >
          Add Query
        </button>
        <button
          onClick={saveAndRun}
          disabled={saving || queries.length === 0}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? "Starting..." : "Run Research"}
        </button>
      </div>
    </div>
  );
}

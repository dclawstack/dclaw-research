"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, Source } from "@/lib/api";

export default function LivePage() {
  const { id } = useParams<{ id: string }>();
  const [sources, setSources] = useState<Source[]>([]);
  const [status, setStatus] = useState<string>("searching");
  const [progress, setProgress] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      api<{ status: string; progress: Record<string, unknown> | null }>(
        `/research/${id}/status`
      )
        .then((data) => {
          setStatus(data.status);
          setProgress(data.progress);
        })
        .catch(console.error);

      api<Source[]>(`/research/${id}/sources?limit=100`)
        .then(setSources)
        .catch(console.error);
    }, 3000);

    return () => clearInterval(interval);
  }, [id]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h2 className="text-xl font-bold mb-4">Discovered Sources</h2>
        <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-2">
          {sources.length === 0 && (
            <p className="text-muted-foreground text-sm">No sources yet...</p>
          )}
          {sources.map((s) => (
            <div key={s.id} className="rounded-lg border p-3">
              <div className="font-medium text-sm line-clamp-1">
                {s.title || s.url}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {s.domain} • Credibility: {Math.round(s.credibility_score * 100)}%
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-bold mb-4">Progress</h2>
        <div className="rounded-lg border p-4">
          <div className="text-sm font-medium mb-2 capitalize">{status}</div>
          {progress && (
            <div className="text-sm text-muted-foreground">
              <div>{String(progress.message || "")}</div>
              <div className="mt-2 h-2 w-full rounded-full bg-muted">
                <div
                  className="h-2 rounded-full bg-primary transition-all"
                  style={{ width: `${Math.min(100, Math.max(0, Number(progress.percent) || 0))}%` }}
                />
              </div>
            </div>
          )}
          {status === "done" && (
            <div className="mt-4 flex gap-2">
              <a
                href={`/research/${id}/report`}
                className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                View Report
              </a>
              <a
                href={`/research/${id}/graph`}
                className="rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-muted"
              >
                View Graph
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

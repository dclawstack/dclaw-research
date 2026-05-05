"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Project } from "@/lib/api";

export default function LibraryPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Project[]>("/research?limit=50")
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Research Library</h1>
      {loading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : projects.length === 0 ? (
        <p className="text-muted-foreground">No research projects yet.</p>
      ) : (
        <div className="grid gap-4">
          {projects.map((p) => (
            <Link
              key={p.id}
              href={`/research/${p.id}/report`}
              className="block rounded-lg border p-4 hover:bg-muted transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold">{p.title}</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {p.template_type} • {p.status}
                  </div>
                </div>
                <div className="text-xs text-muted-foreground">
                  {new Date(p.created_at).toLocaleDateString()}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import { Source } from "@/lib/api";

export default function SourceCard({ source }: { source: Source }) {
  return (
    <div className="rounded-lg border p-3 hover:bg-muted transition-colors">
      <div className="font-medium text-sm line-clamp-1">
        {source.title || source.url}
      </div>
      <div className="text-xs text-muted-foreground mt-1">
        {source.domain} • Credibility: {Math.round(source.credibility_score * 100)}%
      </div>
      {source.author && (
        <div className="text-xs text-muted-foreground">By {source.author}</div>
      )}
    </div>
  );
}

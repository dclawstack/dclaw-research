"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, Project } from "@/lib/api";

export default function NewResearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [template, setTemplate] = useState("academic");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const project = await api<Project>("/research", {
        method: "POST",
        body: JSON.stringify({ query, template_type: template }),
      });
      router.push(`/research/${project.id}/plan`);
    } catch (err) {
      alert("Failed to create research: " + (err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto mt-16">
      <h1 className="text-3xl font-bold mb-2">Deep Research</h1>
      <p className="text-muted-foreground mb-8">
        Enter a research question. We will plan, search, synthesize, and write a
        structured report with verifiable citations.
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Research Question</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="e.g., What are the latest advances in solid-state battery technology?"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Template</label>
          <select
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="academic">Academic Paper</option>
            <option value="business">Business Brief</option>
            <option value="investment">Investment Memo</option>
            <option value="comparison">Product Comparison</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? "Creating..." : "Start Research"}
        </button>
      </form>
    </div>
  );
}

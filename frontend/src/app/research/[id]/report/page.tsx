"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import { api, ReportSection } from "@/lib/api";

const ReportEditor = dynamic(
  () => import("@/components/report-editor/report-editor"),
  { ssr: false }
);

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const [sections, setSections] = useState<ReportSection[]>([]);
  const [markdown, setMarkdown] = useState("");
  const [title, setTitle] = useState("");

  useEffect(() => {
    api<{
      project_id: string;
      title: string;
      markdown: string;
      sections: ReportSection[];
    }>(`/research/${id}/report`)
      .then((data) => {
        setTitle(data.title);
        setMarkdown(data.markdown);
        setSections(data.sections);
      })
      .catch(console.error);
  }, [id]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">{title || "Report"}</h1>
      <div className="mb-4 flex gap-2">
        <a
          href={`/research/${id}/graph`}
          className="text-sm rounded-md border px-3 py-1 hover:bg-muted"
        >
          View Graph
        </a>
        <button
          onClick={() => {
            const blob = new Blob([markdown], { type: "text/markdown" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${title || "report"}.md`;
            a.click();
            URL.revokeObjectURL(url);
          }}
          className="text-sm rounded-md border px-3 py-1 hover:bg-muted"
        >
          Export MD
        </button>
      </div>
      <ReportEditor
        sections={sections}
        onChange={setSections}
        projectId={id}
      />
    </div>
  );
}

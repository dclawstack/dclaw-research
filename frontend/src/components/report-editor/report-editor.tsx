"use client";

import { useState } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Placeholder from "@tiptap/extension-placeholder";
import { api, ReportSection } from "@/lib/api";

function TipTapEditor({
  content,
  onUpdate,
}: {
  content: string;
  onUpdate: (html: string) => void;
}) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({ openOnClick: false }),
      Placeholder.configure({ placeholder: "Write your section content..." }),
    ],
    content: content
      .split("\n")
      .map((line) =>
        line.startsWith("#")
          ? `<h${line.match(/^(#+)/)?.[0].length}>${line.replace(/^#+\s*/, "")}</h${line.match(/^(#+)/)?.[0].length}>`
          : `<p>${line}</p>`
      )
      .join(""),
    onUpdate: ({ editor }) => {
      onUpdate(editor.getHTML());
    },
  });

  if (!editor) return null;

  return (
    <div className="rounded-md border bg-background p-3">
      <div className="mb-2 flex gap-1">
        <button
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={`rounded border px-2 py-1 text-xs ${editor.isActive("bold") ? "bg-muted" : ""}`}
        >
          Bold
        </button>
        <button
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={`rounded border px-2 py-1 text-xs ${editor.isActive("italic") ? "bg-muted" : ""}`}
        >
          Italic
        </button>
        <button
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={`rounded border px-2 py-1 text-xs ${editor.isActive("heading", { level: 2 }) ? "bg-muted" : ""}`}
        >
          H2
        </button>
        <button
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={`rounded border px-2 py-1 text-xs ${editor.isActive("bulletList") ? "bg-muted" : ""}`}
        >
          List
        </button>
      </div>
      <EditorContent
        editor={editor}
        className="max-w-none min-h-[120px] focus:outline-none text-sm"
      />
    </div>
  );
}

function htmlToMarkdown(html: string): string {
  return html
    .replace(/<h1>(.*?)<\/h1>/gi, "# $1\n")
    .replace(/<h2>(.*?)<\/h2>/gi, "## $1\n")
    .replace(/<h3>(.*?)<\/h3>/gi, "### $1\n")
    .replace(/<p>(.*?)<\/p>/gi, "$1\n")
    .replace(/<strong>(.*?)<\/strong>/gi, "**$1**")
    .replace(/<em>(.*?)<\/em>/gi, "*$1*")
    .replace(/<li>(.*?)<\/li>/gi, "- $1\n")
    .replace(/<ul>(.*?)<\/ul>/gis, "$1")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .trim();
}

export default function ReportEditor({
  sections: initialSections,
  onChange,
  projectId,
}: {
  sections: ReportSection[];
  onChange: (sections: ReportSection[]) => void;
  projectId: string;
}) {
  const [saving, setSaving] = useState(false);

  function updateSection(index: number, patch: Partial<ReportSection>) {
    const next = initialSections.map((s, i) =>
      i === index ? { ...s, ...patch } : s
    );
    onChange(next);
  }

  async function save() {
    setSaving(true);
    try {
      await api(`/research/${projectId}/report`, {
        method: "PUT",
        body: JSON.stringify(initialSections),
      });
      alert("Saved");
    } catch (err) {
      alert("Save failed: " + (err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      {initialSections.map((sec, i) => (
        <div key={sec.id || i} className="rounded-lg border p-4">
          <input
            value={sec.heading}
            onChange={(e) => updateSection(i, { heading: e.target.value })}
            className="w-full font-semibold text-lg border-b pb-1 mb-2 focus:outline-none bg-transparent"
          />
          <TipTapEditor
            content={sec.content_markdown}
            onUpdate={(html) =>
              updateSection(i, { content_markdown: htmlToMarkdown(html) })
            }
          />
          {sec.citations.length > 0 && (
            <div className="mt-2 text-xs text-muted-foreground">
              Citations: {sec.citations.join(", ")}
            </div>
          )}
        </div>
      ))}
      <button
        onClick={save}
        disabled={saving}
        className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save Report"}
      </button>
    </div>
  );
}

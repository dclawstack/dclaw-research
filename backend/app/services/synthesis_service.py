"""LLM synthesis and report generation."""

import json
import re
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.research import ResearchProject, Source, Claim, ReportSection, SearchQuery
from app.services.search_service import _credibility_heuristic


async def _ollama_generate(prompt: str, model: str | None = None) -> str:
    """Generate text via Ollama API."""
    model = model or settings.ollama_model
    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return resp.json().get("response", "")


async def _openrouter_generate(prompt: str) -> str:
    """Generate text via OpenRouter fallback."""
    if not settings.openrouter_api_key:
        return ""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openrouter_model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def generate_text(prompt: str, model: str | None = None) -> str:
    """Generate text preferring Ollama, falling back to OpenRouter."""
    try:
        return await _ollama_generate(prompt, model)
    except Exception:
        try:
            return await _openrouter_generate(prompt)
        except Exception:
            return ""


async def generate_research_plan(query: str) -> list[str]:
    """Generate a list of search queries for a research question."""
    prompt = (
        f"You are a research strategist. Given the user query below, generate 5-8 targeted "
        f"search queries that will help build a comprehensive answer. Output ONLY a JSON array of strings.\n\n"
        f"Query: {query}\n\nJSON array:"
    )
    text = await generate_text(prompt)
    # Extract JSON array
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Fallback: split by lines
    lines = [l.strip().strip("-\"'*") for l in text.splitlines() if l.strip()]
    return lines[:8] if lines else [query]


async def summarize_source(text: str, url: str) -> dict[str, Any]:
    """Summarize a source and extract key claims."""
    truncated = text[:12000]
    prompt = (
        f"Summarize the following article and extract up to 5 key claims. "
        f"Output ONLY valid JSON with keys 'summary' (string) and 'claims' (list of strings).\n\n"
        f"Article:\n{truncated}\n\nJSON:"
    )
    result_text = await generate_text(prompt)
    match = re.search(r"\{.*?\}", result_text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return {
                "summary": data.get("summary", ""),
                "claims": data.get("claims", []),
            }
        except json.JSONDecodeError:
            pass
    return {"summary": result_text[:2000], "claims": []}


REPORT_TEMPLATES: dict[str, str] = {
    "academic": (
        "Write an academic-style report with: Abstract, Introduction, Literature Review, "
        "Methodology, Findings, Discussion, Conclusion, and References. Use markdown headers."
    ),
    "business": (
        "Write a business brief with: Executive Summary, Background, Key Findings, "
        "Strategic Implications, Recommendations, and Risk Assessment. Use markdown headers."
    ),
    "investment": (
        "Write an investment memo with: Investment Thesis, Market Overview, Competitive Landscape, "
        "Financial Outlook, Risks, and Recommendation. Use markdown headers."
    ),
    "comparison": (
        "Write a product comparison report with: Overview, Criteria, Side-by-side Comparison Table, "
        "Strengths/Weaknesses, and Verdict. Use markdown headers."
    ),
}


async def generate_report(
    project: ResearchProject, sources: list[Source], claims: list[Claim]
) -> str:
    """Generate the final markdown report."""
    template_instruction = REPORT_TEMPLATES.get(
        project.template_type, REPORT_TEMPLATES["academic"]
    )

    source_texts = []
    for s in sources:
        source_texts.append(
            f"Source [{s.id}]: {s.title}\nURL: {s.url}\n{s.full_text[:3000]}\n"
        )
    combined_sources = "\n---\n".join(source_texts)

    claims_text = "\n".join(
        f"- {c.claim_text} (from source {c.source_id})" for c in claims[:30]
    )

    prompt = (
        f"You are writing a research report for the query: {project.query}\n\n"
        f"Template instructions: {template_instruction}\n\n"
        f"Sources:\n{combined_sources}\n\n"
        f"Extracted Claims:\n{claims_text}\n\n"
        f"Requirements:\n"
        f"1. Every factual statement must include an inline citation like [source:ID].\n"
        f"2. Flag any contradictory claims.\n"
        f"3. Write in clear, professional markdown.\n\n"
        f"Report:"
    )

    return await generate_text(prompt)


async def generate_sections_from_markdown(
    project_id: UUID, markdown: str
) -> list[dict[str, Any]]:
    """Parse markdown into report sections."""
    sections = []
    pattern = re.compile(r"^(#{1,3})\s+(.*?)\n(.*?)(?=\n#{1,3}\s+|\Z)", re.DOTALL | re.MULTILINE)
    for m in pattern.finditer(markdown):
        heading = m.group(2).strip()
        content = m.group(3).strip()
        # Extract citation UUIDs
        citation_ids = re.findall(r"\[source:([a-f0-9\-]{36})\]", content)
        sections.append({
            "project_id": project_id,
            "heading": heading,
            "content_markdown": content,
            "citations": [UUID(cid) for cid in citation_ids],
            "sort_order": len(sections),
        })
    if not sections:
        sections.append({
            "project_id": project_id,
            "heading": "Report",
            "content_markdown": markdown,
            "citations": [],
            "sort_order": 0,
        })
    return sections

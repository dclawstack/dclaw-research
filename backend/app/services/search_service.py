"""Web search and scraping services."""

import asyncio
import json
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup

from app.core.config import settings


def _extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or ""


def _credibility_heuristic(url: str, publish_date: datetime | None) -> float:
    """Compute a rough credibility score based on domain and recency."""
    domain = _extract_domain(url).lower()
    score = 0.5

    # Domain reputation boost
    trusted_domains = {
        "arxiv.org", "pubmed.ncbi.nlm.nih.gov", "nature.com", "science.org",
        "ieee.org", "acm.org", "who.int", "un.org", "worldbank.org",
        "reuters.com", "bloomberg.com", "ft.com", "wsj.com",
        "techcrunch.com", "theverge.com", "github.com",
    }
    if any(td in domain for td in trusted_domains):
        score += 0.3

    # Recency boost
    if publish_date:
        age_days = (datetime.now(publish_date.tzinfo) - publish_date).days
        if age_days < 30:
            score += 0.2
        elif age_days < 365:
            score += 0.1

    return min(1.0, score)


async def search_firecrawl(query: str) -> list[dict[str, Any]]:
    """Search using Firecrawl API."""
    if not settings.firecrawl_api_key:
        return []

    url = "https://api.firecrawl.dev/v1/search"
    headers = {"Authorization": f"Bearer {settings.firecrawl_api_key}"}
    payload = {"query": query, "limit": 10}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("data", []):
        results.append({
            "url": item.get("url", ""),
            "title": item.get("title", ""),
            "snippet": item.get("description", ""),
        })
    return results


async def search_searxng(query: str) -> list[dict[str, Any]]:
    """Search using local SearXNG instance."""
    if not settings.searxng_url:
        return []

    params = {"q": query, "format": "json", "engines": "google,bing,duckduckgo"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{settings.searxng_url}/search", params=params)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("results", [])[:10]:
        results.append({
            "url": item.get("url", ""),
            "title": item.get("title", ""),
            "snippet": item.get("content", ""),
        })
    return results


async def scrape_with_trafilatura(url: str) -> dict[str, Any]:
    """Scrape a single URL using trafilatura."""
    try:
        downloaded = await asyncio.to_thread(trafilatura.fetch_url, url)
        if not downloaded:
            return {"url": url, "title": "", "text": "", "author": "", "date": None}

        result = await asyncio.to_thread(
            trafilatura.extract,
            downloaded,
            output_format="json",
            with_metadata=True,
            include_comments=False,
            include_tables=True,
        )
        if not result:
            return {"url": url, "title": "", "text": "", "author": "", "date": None}

        data = json.loads(result) if isinstance(result, str) else (result if isinstance(result, dict) else {})
        raw_date = data.get("date")
        date = None
        if raw_date:
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d %B %Y"):
                try:
                    date = datetime.strptime(raw_date, fmt)
                    break
                except ValueError:
                    continue

        return {
            "url": url,
            "title": data.get("title", ""),
            "text": data.get("text", ""),
            "author": data.get("author", ""),
            "date": date,
        }
    except Exception:
        return {"url": url, "title": "", "text": "", "author": "", "date": None}


async def scrape_with_jina(url: str) -> dict[str, Any]:
    """Scrape a single URL using Jina AI reader."""
    headers = {}
    if settings.jina_api_key:
        headers["Authorization"] = f"Bearer {settings.jina_api_key}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"https://r.jina.ai/http://{url}" if not url.startswith("http") else f"https://r.jina.ai/{url}",
            headers=headers,
        )
        if resp.status_code != 200:
            return {"url": url, "title": "", "text": "", "author": "", "date": None}

    text = resp.text
    title = ""
    lines = text.splitlines()
    if lines and lines[0].startswith("Title:"):
        title = lines[0].replace("Title:", "").strip()
        text = "\n".join(lines[1:])

    return {
        "url": url,
        "title": title,
        "text": text,
        "author": "",
        "date": None,
    }


async def scrape_url(url: str) -> dict[str, Any]:
    """Scrape a URL trying multiple methods."""
    result = await scrape_with_trafilatura(url)
    if len(result.get("text", "")) > 500:
        return result
    result = await scrape_with_jina(url)
    return result


async def run_search(query: str) -> list[dict[str, Any]]:
    """Run search across configured providers and deduplicate."""
    tasks = [search_firecrawl(query), search_searxng(query)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    seen = set()
    combined = []
    for rlist in results:
        if isinstance(rlist, Exception):
            continue
        for item in rlist:
            url = item.get("url", "")
            if url and url not in seen:
                seen.add(url)
                combined.append(item)
    return combined

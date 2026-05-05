"""Shared Redis client for progress and caching."""

import json
from typing import Any

import redis
from app.core.config import settings

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def set_progress(project_id: str, payload: dict[str, Any]) -> None:
    r = get_redis()
    key = f"research:{project_id}:progress"
    r.set(key, json.dumps(payload), ex=3600)


def get_progress(project_id: str) -> dict[str, Any] | None:
    r = get_redis()
    key = f"research:{project_id}:progress"
    raw = r.get(key)
    if raw:
        try:
            return json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
        except Exception:
            return None
    return None

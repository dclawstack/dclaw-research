"""Research API v1 routes."""

from fastapi import APIRouter
from app.api.v1.research.research import router as research_router
from app.api.v1.research.sources import router as sources_router
from app.api.v1.research.graph import router as graph_router
from app.api.v1.research.report import router as report_router

router = APIRouter()
router.include_router(research_router, prefix="/research")
router.include_router(sources_router, prefix="/research")
router.include_router(graph_router, prefix="/research")
router.include_router(report_router, prefix="/research")

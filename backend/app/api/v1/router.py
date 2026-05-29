"""Gom tất cả router API v1."""

from fastapi import APIRouter

from app.api.v1 import agent, auth, cards, lab, rag, settings

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(settings.router)
router.include_router(agent.router)
router.include_router(cards.router)
router.include_router(rag.router)
router.include_router(lab.router)

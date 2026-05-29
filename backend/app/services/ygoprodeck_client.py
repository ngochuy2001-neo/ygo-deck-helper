"""HTTP client cho YGOPRODeck API v7."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.ygoprodeck import (
    YgoCardInfoResponse,
    YgoDbVersionResponse,
)


class YgoProDeckClient:
    """Client gọi YGOPRODeck với throttle để tránh vượt rate limit."""

    def __init__(self) -> None:
        self._base = settings.YGOPRODECK_API_BASE.rstrip("/")
        self._delay = settings.CARD_SYNC_REQUEST_DELAY_MS / 1000.0
        self._lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def _throttle(self) -> None:
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request_at
            if elapsed < self._delay:
                await asyncio.sleep(self._delay - elapsed)
            self._last_request_at = asyncio.get_event_loop().time()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        await self._throttle()
        url = f"{self._base}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1.0 * (attempt + 1))
        raise RuntimeError("Unreachable")

    async def get_db_version(self) -> YgoDbVersionResponse:
        data = await self._get("checkDBVer.php")
        if isinstance(data, list) and data:
            return YgoDbVersionResponse.model_validate(data[0])
        if isinstance(data, dict):
            return YgoDbVersionResponse.model_validate(data)
        raise ValueError("checkDBVer response không hợp lệ")

    async def fetch_cards_page(
        self,
        *,
        num: int,
        offset: int,
        misc: bool = True,
    ) -> YgoCardInfoResponse:
        params: dict[str, Any] = {"num": num, "offset": offset}
        if misc:
            params["misc"] = "yes"
        data = await self._get("cardinfo.php", params=params)
        if isinstance(data, dict) and "error" in data:
            raise ValueError(data["error"])
        return YgoCardInfoResponse.model_validate(data)

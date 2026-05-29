"""Service đọc/ghi cấu hình LM Studio và kiểm tra kết nối."""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from app.core.config import settings
from app.schemas.lm_studio import (
    LMStudioModelInfo,
    LMStudioSettings,
    LMStudioSettingsUpdate,
    LMStudioStatusResponse,
)


def _config_path() -> Path:
    return settings.lm_studio_config_path


def load_lm_studio_settings() -> LMStudioSettings:
    """Đọc cấu hình từ JSON; tạo file mặc định nếu chưa có."""
    path = _config_path()
    if not path.exists():
        default = LMStudioSettings()
        save_lm_studio_settings(default)
        return default

    raw = json.loads(path.read_text(encoding="utf-8"))
    return LMStudioSettings.model_validate(raw)


def save_lm_studio_settings(config: LMStudioSettings) -> LMStudioSettings:
    """Ghi cấu hình ra JSON."""
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config.model_dump_json(indent=2), encoding="utf-8")
    return config


def update_lm_studio_settings(payload: LMStudioSettingsUpdate) -> LMStudioSettings:
    """Merge cập nhật một phần vào config hiện tại."""
    current = load_lm_studio_settings()
    updates = payload.model_dump(exclude_unset=True)
    merged = current.model_copy(update=updates)
    return save_lm_studio_settings(merged)


async def fetch_lm_studio_models(config: LMStudioSettings | None = None) -> list[LMStudioModelInfo]:
    """Lấy danh sách model từ LM Studio OpenAI-compatible API."""
    cfg = config or load_lm_studio_settings()
    url = f"{cfg.base_url}/models"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {cfg.api_key}"},
        )
        response.raise_for_status()
        data = response.json()

    models: list[LMStudioModelInfo] = []
    for item in data.get("data", []):
        model_id = item.get("id", "")
        if model_id:
            models.append(LMStudioModelInfo(id=model_id, name=item.get("name")))

    return models


async def check_lm_studio_status(config: LMStudioSettings | None = None) -> LMStudioStatusResponse:
    """Kiểm tra LM Studio có phản hồi và model đã chọn có tồn tại không."""
    cfg = config or load_lm_studio_settings()

    try:
        models = await fetch_lm_studio_models(cfg)
    except httpx.HTTPError as exc:
        return LMStudioStatusResponse(
            connected=False,
            base_url=cfg.base_url,
            model_name=cfg.model_name,
            message=f"Không kết nối được LM Studio tại {cfg.base_url}: {exc}",
            models_count=0,
        )

    if not cfg.model_name.strip():
        return LMStudioStatusResponse(
            connected=True,
            base_url=cfg.base_url,
            model_name=cfg.model_name,
            message="Đã kết nối LM Studio. Chưa chọn model — hãy chọn trong Settings.",
            models_count=len(models),
        )

    model_ids = {m.id for m in models}
    if cfg.model_name not in model_ids:
        return LMStudioStatusResponse(
            connected=True,
            base_url=cfg.base_url,
            model_name=cfg.model_name,
            message=(
                f"Đã kết nối nhưng model '{cfg.model_name}' không có trong danh sách. "
                "Hãy load model trong LM Studio hoặc chọn model khác."
            ),
            models_count=len(models),
        )

    return LMStudioStatusResponse(
        connected=True,
        base_url=cfg.base_url,
        model_name=cfg.model_name,
        message="Kết nối LM Studio thành công. Model sẵn sàng.",
        models_count=len(models),
    )

"""API cấu hình LM Studio — đọc/ghi config và kiểm tra trạng thái."""

import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.lm_studio import (
    LMStudioModelsResponse,
    LMStudioSettings,
    LMStudioSettingsUpdate,
    LMStudioStatusResponse,
)
from app.services.lm_studio_service import (
    check_lm_studio_status,
    fetch_lm_studio_models,
    load_lm_studio_settings,
    update_lm_studio_settings,
)

router = APIRouter(prefix="/settings/lm-studio", tags=["settings"])


@router.get("", response_model=LMStudioSettings)
async def get_lm_studio_settings() -> LMStudioSettings:
    """Lấy cấu hình LM Studio hiện tại."""
    return load_lm_studio_settings()


@router.put("", response_model=LMStudioSettings)
async def put_lm_studio_settings(payload: LMStudioSettingsUpdate) -> LMStudioSettings:
    """Cập nhật cấu hình LM Studio (host, port, model, api_key)."""
    return update_lm_studio_settings(payload)


@router.get("/status", response_model=LMStudioStatusResponse)
async def get_lm_studio_status() -> LMStudioStatusResponse:
    """Kiểm tra kết nối tới LM Studio và model đã chọn."""
    return await check_lm_studio_status()


@router.get("/models", response_model=LMStudioModelsResponse)
async def get_lm_studio_models() -> LMStudioModelsResponse:
    """Lấy danh sách model từ LM Studio tại host/port đã cấu hình."""
    try:
        models = await fetch_lm_studio_models()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Không lấy được danh sách model từ LM Studio: {exc}",
        ) from exc

    return LMStudioModelsResponse(models=models)

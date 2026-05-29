"""Đọc/ghi cấu hình LM Studio dùng chung giữa agents và backend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from agentscope.credential import OpenAICredential
from agentscope.model import OpenAIChatModel

CONFIG_PATH = Path(__file__).resolve().parent / "lm_studio.json"


class LMStudioConfig(BaseModel):
    """Cấu hình kết nối LM Studio (OpenAI-compatible API)."""

    host: str = Field(default="127.0.0.1", description="IP hoặc hostname LM Studio")
    port: int = Field(default=1234, ge=1, le=65535, description="Cổng API LM Studio")
    model_name: str = Field(default="", description="ID model đang load trong LM Studio")
    api_key: str = Field(default="lm-studio", description="API key (LM Studio không validate)")

    def base_url(self) -> str:
        """URL gốc OpenAI-compatible, ví dụ http://127.0.0.1:1234/v1."""
        return f"http://{self.host}:{self.port}/v1"


def get_base_url(config: LMStudioConfig | None = None) -> str:
    """Trả về base_url từ config hiện tại hoặc config truyền vào."""
    cfg = config or load_config()
    return cfg.base_url()


def load_config(path: Path | None = None) -> LMStudioConfig:
    """Đọc cấu hình từ JSON; tạo file mặc định nếu chưa tồn tại."""
    config_path = path or CONFIG_PATH
    if not config_path.exists():
        default = LMStudioConfig()
        save_config(default, path=config_path)
        return default

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return LMStudioConfig.model_validate(raw)


def save_config(config: LMStudioConfig, path: Path | None = None) -> LMStudioConfig:
    """Ghi cấu hình ra JSON và trả về config đã lưu."""
    config_path = path or CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        config.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return config


def create_openai_chat_model(
    config: LMStudioConfig | None = None,
    *,
    stream: bool = False,
    **parameters: Any,
) -> OpenAIChatModel:
    """
    Tạo OpenAIChatModel trỏ tới LM Studio theo cấu hình hiện tại.

    Raises:
        ValueError: Khi chưa chọn model_name.
    """
    cfg = config or load_config()
    if not cfg.model_name.strip():
        raise ValueError(
            "Chưa chọn model. Hãy cấu hình model_name trong Settings hoặc lm_studio.json."
        )

    credential = OpenAICredential(
        api_key=cfg.api_key,
        base_url=cfg.base_url(),
    )
    model_params = OpenAIChatModel.Parameters(**parameters) if parameters else None

    return OpenAIChatModel(
        credential=credential,
        model=cfg.model_name,
        parameters=model_params,
        stream=stream,
    )

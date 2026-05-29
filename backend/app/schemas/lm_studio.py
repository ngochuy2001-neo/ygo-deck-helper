"""Pydantic schemas cho cấu hình LM Studio."""

from pydantic import BaseModel, Field


class LMStudioSettings(BaseModel):
    """Cấu hình kết nối LM Studio."""

    host: str = Field(default="127.0.0.1", description="IP hoặc hostname LM Studio")
    port: int = Field(default=1234, ge=1, le=65535, description="Cổng API LM Studio")
    model_name: str = Field(default="", description="ID model đang load trong LM Studio")
    api_key: str = Field(default="lm-studio", description="API key (LM Studio không validate)")

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/v1"


class LMStudioSettingsUpdate(BaseModel):
    """Body cập nhật cấu hình — các field đều optional."""

    host: str | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    model_name: str | None = None
    api_key: str | None = None


class LMStudioModelInfo(BaseModel):
    """Model trả về từ LM Studio GET /v1/models."""

    id: str
    name: str | None = None


class LMStudioModelsResponse(BaseModel):
    models: list[LMStudioModelInfo]


class LMStudioStatusResponse(BaseModel):
    connected: bool
    base_url: str
    model_name: str
    message: str
    models_count: int = 0


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class AgentChatResponse(BaseModel):
    reply: str
    model_name: str

"""FunctionTool tự động ALLOW — phù hợp API backend không có human-in-the-loop."""

from __future__ import annotations

import inspect
from typing import Any

from agentscope.message import TextBlock
from agentscope.permission import PermissionBehavior, PermissionDecision
from agentscope.tool import FunctionTool, ToolChunk


class AllowedFunctionTool(FunctionTool):
    """Tool Python được phép chạy ngay, không cần xác nhận từ UI."""

    async def check_permissions(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW,
            message="Auto-allowed for server-side agent.",
        )

    async def __call__(self, **kwargs: Any) -> ToolChunk | AsyncGenerator[ToolChunk, None]:
        """Gọi hàm gốc và bọc kết quả string thành ToolChunk (AgentScope 2)."""
        if inspect.iscoroutinefunction(self._func):
            result = await self._func(**kwargs)
        else:
            result = self._func(**kwargs)

        if isinstance(result, ToolChunk):
            return result
        if inspect.isasyncgen(result) or inspect.isgenerator(result):
            return result

        text = result if isinstance(result, str) else str(result)
        return ToolChunk(content=[TextBlock(text=text)])

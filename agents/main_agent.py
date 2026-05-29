#!/usr/bin/env python3
"""
Điểm khởi chạy (entrypoint) CLI cho hệ thống Agent YGO Deck Helper.

Usage:
    python main_agent.py "Tìm thông tin lá bài Dark Magician."
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Đảm bảo import module nội bộ khi chạy từ thư mục agents/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.message import UserMsg

from config.lm_studio import load_config
from workflows.react_deck_agent import create_deck_helper_agent, extract_text_from_msg


async def run_agent(message: str) -> str:
    """Chạy DeckHelper agent với tin nhắn người dùng."""
    config = load_config()
    if not config.model_name.strip():
        raise ValueError(
            "Chưa chọn model. Cập nhật agents/config/lm_studio.json "
            "hoặc dùng trang Settings trên frontend."
        )

    agent = create_deck_helper_agent(config)
    reply = await agent.reply(UserMsg(name="user", content=message))
    return extract_text_from_msg(reply)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="YGO Deck Helper Agent — CLI entrypoint"
    )
    parser.add_argument(
        "message",
        nargs="?",
        default="",
        help="Tin nhắn gửi tới agent",
    )
    args = parser.parse_args()

    if not args.message.strip():
        print('Usage: python main_agent.py "<your message>"', file=sys.stderr)
        sys.exit(1)

    try:
        response = asyncio.run(run_agent(args.message.strip()))
        print(response)
    except ValueError as exc:
        print(f"Lỗi cấu hình: {exc}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:  # noqa: BLE001 — CLI cần bắt lỗi kết nối LM Studio
        print(f"Lỗi agent: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

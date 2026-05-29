"""Các công cụ (tools) mà Agent có thể gọi thông qua Function Calling."""

from tools.web_search import web_search
from tools.db_queries import query_card_database

__all__ = ["web_search", "query_card_database"]

"""Tool tìm kiếm web — stub cho Agent Function Calling."""


async def web_search(query: str, max_results: int = 5) -> str:
    """
    Tìm kiếm thông tin trên web liên quan đến Yu-Gi-Oh! hoặc chủ đề deck building.

    Dùng khi Agent cần tra cứu meta mới nhất, rulings, hoặc thông tin không có
    trong database nội bộ.

    Args:
        query: Câu truy vấn tìm kiếm (tiếng Việt hoặc tiếng Anh).
        max_results: Số kết quả tối đa trả về (mặc định 5, tối đa 10).

    Returns:
        Chuỗi JSON hoặc text tóm tắt kết quả tìm kiếm. Trả về thông báo lỗi
        dạng string nếu request thất bại để Agent tự sửa (self-correction).
    """
    return (
        f"[STUB] web_search chưa được triển khai. "
        f"Query: {query!r}, max_results={max_results}"
    )

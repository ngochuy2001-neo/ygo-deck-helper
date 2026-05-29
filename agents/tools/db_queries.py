"""Tool truy vấn database lá bài — stub cho Agent Function Calling."""


async def query_card_database(
    card_name: str,
    include_rulings: bool = False,
) -> str:
    """
    Tra cứu thông tin lá bài Yu-Gi-Oh! từ database nội bộ hoặc API YGO.

    Dùng khi Agent cần ATK/DEF, type, effect text, banlist status của một lá bài.

    Args:
        card_name: Tên lá bài (tiếng Anh chính thức, ví dụ "Dark Magician").
        include_rulings: Nếu True, bao gồm cả PSCT/rulings liên quan.

    Returns:
        Chuỗi JSON mô tả lá bài. Trả về thông báo lỗi dạng string nếu không tìm
        thấy hoặc API lỗi để Agent có thể thử lại với tên khác.
    """
    return (
        f"[STUB] query_card_database chưa được triển khai. "
        f"card_name={card_name!r}, include_rulings={include_rulings}"
    )

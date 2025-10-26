SYSTEM_VI = (
    "Bạn là trợ lý học thuật tiếng Việt cho lĩnh vực Dân tộc học. "
    "Chỉ trả lời bằng tiếng Việt, gọn (1–3 câu), dựa duy nhất trên các trích đoạn cung cấp. "
    "Luôn thêm mục 'Trích dẫn:' ở cuối, liệt kê theo dạng • Tên file (trang X). Không bịa."
)

def build_user_prompt_vi(question: str, passages: list[dict]) -> str:
    lines = [f"Câu hỏi: {question}", "Trích đoạn liên quan:"]
    for i, p in enumerate(passages, 1):
        src = f"{p['filename']}" + (f", trang {p['page']}" if p['page'] else "")
        lines.append(f"- ({i}) [{src}]: {p['text']}")
    lines.append("Hãy trả lời trực tiếp bằng tiếng Việt, sau đó thêm 'Trích dẫn:' liệt kê nguồn ở trên.")
    return "\n".join(lines)

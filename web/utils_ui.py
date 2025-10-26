import os
import requests
from typing import List, Dict, Optional

API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")

def api_health() -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=10)
        return r.ok
    except Exception:
        return False

def api_ask(question: str, top_k: int = 3) -> Dict:
    """Gọi API /ask của FastAPI, trả về dict: {answer, citations}"""
    payload = {"question": question, "top_k": top_k}
    r = requests.post(f"{API_BASE_URL}/ask", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def api_upload_file(file_tuple) -> Dict:
    """Upload (filename, fileobj, mimetype) -> API /upload"""
    files = {"file": file_tuple}
    r = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=120)
    r.raise_for_status()
    return r.json()

# ====== LLM client tại WebApp (tạo 'câu hỏi thảo luận') ======
def llm_synthesize_from_questions(questions: List[str]) -> str:
    """
    Sinh 'Câu hỏi thảo luận' từ danh sách 10 câu hỏi nhỏ (tiếng Việt).
    Ưu tiên Groq; fallback OpenAI nếu đặt LLM_PROVIDER=openai.
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower().strip()
    sys_prompt = (
        "Bạn là trợ lý học thuật tiếng Việt trong lĩnh vực Dân tộc học. "
        "Dựa trên 10 câu hỏi nhỏ đã nêu, hãy tạo **một câu hỏi thảo luận tổng hợp duy nhất**, "
        "yêu cầu người học **tư duy phản biện, liên hệ thực tiễn hoặc so sánh đối chiếu**. "
        "Chỉ **một câu**, **rõ ràng**, **không trùng lặp** với các câu hỏi nhỏ. Trả lời bằng **tiếng Việt**."
    )
    user_prompt = "Danh sách 10 câu hỏi nhỏ:\n" + "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

    try:
        if provider == "groq":
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4, max_tokens=180, top_p=0.9
            )
            return resp.choices[0].message.content.strip()
        else:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            chat = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4, max_tokens=180, top_p=0.9
            )
            return chat.choices[0].message.content.strip()
    except Exception as e:
        return f"(Không thể sinh câu hỏi thảo luận lúc này: {e})"

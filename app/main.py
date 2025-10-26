import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from app.schemas import AskRequest, AskAnswer
from app.ingest import ingest_upload
from app.rag import search_similar
from app.prompts import SYSTEM_VI, build_user_prompt_vi

USE_GROQ = bool(os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

app = FastAPI(title="EthnoAI – RAG tiếng Việt cho Dân tộc học", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        return ingest_upload(file)
    except Exception as e:
        raise HTTPException(400, str(e))

def call_llm_vi(system_prompt: str, user_prompt: str) -> str:
    if USE_GROQ:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        r = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role":"system","content":system_prompt},
                      {"role":"user","content":user_prompt}],
            temperature=0.2, max_tokens=300, top_p=0.9
        )
        return r.choices[0].message.content.strip()
    elif USE_OPENAI:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        r = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role":"system","content":system_prompt},
                      {"role":"user","content":user_prompt}],
            temperature=0.2, max_tokens=300, top_p=0.9
        )
        return r.choices[0].message.content.strip()
    return "Thiếu GROQ_API_KEY hoặc OPENAI_API_KEY."

@app.post("/ask", response_model=AskAnswer)
def ask(req: AskRequest):
    q = (req.question or "").strip()
    if not q:
        raise HTTPException(400, "Câu hỏi trống.")
    hits = search_similar(q, top_k=max(1, min(5, req.top_k)))
    if not hits:
        return AskAnswer(answer="Không tìm thấy trích đoạn phù hợp để trả lời.", citations=[])
    user_prompt = build_user_prompt_vi(q, hits)
    answer = call_llm_vi(SYSTEM_VI, user_prompt)
    citations = [f"{h['filename']}" + (f" (trang {h['page']})" if h['page'] else "") for h in hits]
    return AskAnswer(answer=answer, citations=citations)

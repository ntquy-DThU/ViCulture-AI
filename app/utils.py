import os, re
import fitz  # PyMuPDF
from docx import Document

MIN_CHARS, MAX_CHARS = 400, 900
_vi_diac = re.compile(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]")

def looks_vietnamese(text: str) -> bool:
    return bool(_vi_diac.search((text or "").lower()))

def chunkify(text: str):
    lines = [ln.strip() for ln in (text or "").split("\n") if ln.strip()]
    chunks, buf = [], ""
    for ln in lines:
        if len(buf) + 1 + len(ln) <= MAX_CHARS:
            buf = (buf + " " + ln).strip()
        else:
            if len(buf) >= MIN_CHARS:
                chunks.append(buf)
            buf = ln
    if len(buf) >= MIN_CHARS:
        chunks.append(buf)
    return chunks or ([text] if text.strip() else [])

def read_pdf(path: str):
    out = []
    doc = fitz.open(path)
    for page_num, page in enumerate(doc, start=1):
        text = (page.get_text("text") or "").strip()
        if not text:
            continue
        for ch in chunkify(text):
            out.append((ch, page_num))
    return out

def read_docx(path: str):
    doc = Document(path)
    txt = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [(ch, None) for ch in chunkify(txt)]

def read_txt(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    return [(ch, None) for ch in chunkify(txt)]

def extract_chunks(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":  return read_pdf(path)
    if ext == ".docx": return read_docx(path)
    if ext == ".txt":  return read_txt(path)
    return []

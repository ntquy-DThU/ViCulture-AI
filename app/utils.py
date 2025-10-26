import os
import smtplib
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from docx import Document
from PyPDF2 import PdfReader


# ============================================================
# 1️⃣ HÀM TRÍCH XUẤT NỘI DUNG FILE THÀNH CHUNK
# ============================================================

def extract_chunks(file_path: str, chunk_size: int = 1000) -> List[str]:
    """
    Tách nội dung file (PDF, DOCX, TXT) thành các đoạn nhỏ (chunks)
    để sử dụng cho hệ thống RAG / hỏi đáp.
    """
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    # ---- TXT ----
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    # ---- DOCX ----
    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # ---- PDF ----
    elif ext == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

    else:
        raise ValueError(f"❌ Định dạng file không được hỗ trợ: {ext}")

    # Làm sạch văn bản
    text = text.replace("\r", " ").replace("\n\n", "\n").strip()

    # Tách thành các đoạn (mỗi đoạn ~1000 ký tự)
    chunks = [text[i:i + chunk_size].strip() for i in range(0, len(text), chunk_size)]
    return [c for c in chunks if c]


# ============================================================
# 2️⃣ HÀM GỬI EMAIL CÂU HỎI THẢO LUẬN
# ============================================================

def send_discussion_email(student_name: str, student_email: str, discussion_question: str) -> bool:
    """
    Gửi email thảo luận tới học viên với câu hỏi tổng hợp.
    Trả về True nếu gửi thành công, False nếu thất bại.
    """
    sender = os.getenv("SMTP_USER", "ntquy@dthu.edu.vn")
    password = os.getenv("SMTP_PASS", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    subject = "Câu hỏi thảo luận từ ViCulture-AI"
    body = f"""
Chào Anh/Chị: {student_name},

Sau khi nhận được 10 câu hỏi của anh/chị, hệ thống đã tạo ra câu hỏi thảo luận như sau:

"{discussion_question}"

Hướng dẫn:
- Trả lời bằng văn phong khoa học, có dẫn chứng từ thực tiễn dân tộc học.
- Liên hệ với tài liệu hoặc trải nghiệm thực tế.
- Dung lượng đề xuất: 300–500 từ.

Chúc các anh/chị làm bài tốt!

Trân trọng,
ViCulture-AI
"""

    # Chuẩn bị email MIME
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = student_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ Email đã gửi thành công đến {student_email}")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi gửi email tới {student_email}: {e}")
        return False

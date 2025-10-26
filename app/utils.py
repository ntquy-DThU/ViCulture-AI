import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_discussion_email(student_name: str, student_email: str, discussion_question: str):
    """Gửi email thảo luận tới học viên"""
    sender = os.getenv("SMTP_USER", "ntquy@dthu.edu.vn")
    password = os.getenv("SMTP_PASS", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    subject = "Câu hỏi thảo luận từ ViCulture-AI"
    body = f"""
Chào Anh/Chị: {student_name},

Sau khi nhận được 10 câu hỏi của anh/chị, hệ thống đưa ra câu hỏi thảo luận để anh/chị làm như sau:

"{discussion_question}"

Hướng dẫn:
- Trả lời bằng văn phong khoa học, có dẫn chứng từ thực tiễn dân tộc học.
- Liên hệ với tài liệu hoặc trải nghiệm thực tế.
- Dung lượng đề xuất: 300–500 từ.

Chúc các anh/chị làm bài tốt.

Trân trọng,
ViCulture-AI
"""

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = student_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, student_email, msg.as_string())
        print(f"✅ Email đã gửi đến {student_email}")
        return True
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")
        return False

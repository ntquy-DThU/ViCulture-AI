import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_discussion_email(student_name: str, student_email: str, discussion_question: str) -> bool:
    """
    Gửi email chứa câu hỏi thảo luận tới học viên.
    Sử dụng tài khoản SMTP được cấu hình qua biến môi trường:
        - SMTP_USER
        - SMTP_PASS
        - SMTP_SERVER
        - SMTP_PORT
    Trả về True nếu gửi thành công, False nếu thất bại.
    """

    # ================== 1️⃣ Cấu hình SMTP ==================
    sender = os.getenv("SMTP_USER", "ntquy@dthu.edu.vn")
    password = os.getenv("SMTP_PASS", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    # ================== 2️⃣ Soạn nội dung email ==================
    subject = "Câu hỏi thảo luận từ ViCulture-AI"
    body = f"""
Chào Anh/Chị: {student_name},

Sau khi nhận được 10 câu hỏi của anh/chị, hệ thống ViCulture-AI đã tạo ra câu hỏi thảo luận như sau:

"{discussion_question}"

Hướng dẫn:
- Trả lời bằng văn phong khoa học, có dẫn chứng từ thực tiễn dân tộc học.
- Liên hệ với tài liệu hoặc trải nghiệm thực tế.
- Dung lượng đề xuất: 300–500 từ.

Chúc các anh/chị làm bài tốt!

Trân trọng,
ViCulture-AI
"""

    # ================== 3️⃣ Tạo đối tượng email ==================
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = student_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # ================== 4️⃣ Gửi email qua SMTP ==================
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Bật mã hóa bảo mật TLS
            server.login(sender, password)
            server.send_message(msg)

        print(f"✅ Email đã được gửi thành công tới {student_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Lỗi xác thực SMTP: Sai mật khẩu hoặc chưa bật quyền truy cập ứng dụng kém an toàn.")
        return False

    except smtplib.SMTPConnectError:
        print("❌ Không thể kết nối đến máy chủ SMTP. Kiểm tra địa chỉ và cổng.")
        return False

    except smtplib.SMTPRecipientsRefused:
        print(f"❌ Địa chỉ email người nhận không hợp lệ: {student_email}")
        return False

    except Exception as e:
        print(f"❌ Lỗi không xác định khi gửi email: {e}")
        return False

from fastapi import APIRouter, File, UploadFile, HTTPException
from app.db import run_sql
import pandas as pd
from werkzeug.security import generate_password_hash
from app.utils_mail import send_discussion_email

router = APIRouter(prefix="/students")

@router.post("/import")
def import_students(file: UploadFile = File(...)):
    try:
        df = pd.read_excel(file.file)
    except Exception:
        raise HTTPException(400, "Không đọc được file Excel.")
    count = 0
    for _, row in df.iterrows():
        fullname = row.get("fullname") or row.get("Họ tên")
        email = row.get("email")
        student_code = row.get("student_code") or row.get("Mã SV")
        if not email or not fullname:
            continue
        hashed = generate_password_hash("123456")
        run_sql("""
            INSERT INTO students(fullname, email, student_code, password_hash)
            VALUES (:n, :e, :c, :p)
            ON CONFLICT (email) DO NOTHING
        """, n=fullname, e=email, c=student_code, p=hashed)
        count += 1
    return {"imported": count}

@router.post("/change-password")
def change_password(email: str, old_pass: str, new_pass: str):
    from werkzeug.security import check_password_hash
    row = run_sql("SELECT password_hash FROM students WHERE email=:e", e=email).first()
    if not row or not check_password_hash(row[0], old_pass):
        raise HTTPException(400, "Sai mật khẩu.")
    hashed = generate_password_hash(new_pass)
    run_sql("UPDATE students SET password_hash=:p WHERE email=:e", p=hashed, e=email)
    return {"message": "Đổi mật khẩu thành công."}

@router.post("/notify-discussion")
def notify_student(name: str, email: str, question: str):
    """Gửi mail chứa câu hỏi thảo luận"""
    ok = send_discussion_email(student_name=name, student_email=email, discussion_question=question)
    if not ok:
        raise HTTPException(status_code=500, detail="Gửi mail thất bại.")
    return {"status": "sent"}

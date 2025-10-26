import os
import tempfile
from fastapi import UploadFile
from app.utils import extract_chunks
from app.rag import insert_document, insert_chunks


def ingest_upload(file: UploadFile):
    """
    Xử lý upload tài liệu:
    - Lưu file tạm thời
    - Trích xuất nội dung thành các đoạn nhỏ (chunks)
    - Ghi vào cơ sở dữ liệu (insert_document & insert_chunks)
    """
    suffix = os.path.splitext(file.filename)[1].lower()

    # Tạo file tạm an toàn
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        temp_path = tmp.name

    try:
        # Thêm metadata vào cơ sở dữ liệu
        doc_id = insert_document(file.filename, file.content_type or "")

        # Trích xuất nội dung văn bản
        chunks = extract_chunks(temp_path)
        if not chunks:
            raise ValueError("Không trích xuất được nội dung tài liệu.")

        # Ghi các đoạn vào DB/vector store
        insert_chunks(doc_id, chunks)

        # Trả kết quả
        return {"doc_id": doc_id, "chunks": len(chunks)}

    finally:
        # Dù có lỗi vẫn đảm bảo xóa file tạm
        if os.path.exists(temp_path):
            os.remove(temp_path)

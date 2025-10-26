import os, tempfile
from fastapi import UploadFile
from app.utils import extract_chunks
from app.rag import insert_document, insert_chunks

def ingest_upload(file: UploadFile):
    suf = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suf) as tmp:
        tmp.write(file.file.read())
        temp_path = tmp.name
    doc_id = insert_document(file.filename, file.content_type or "")
    chunks = extract_chunks(temp_path)
    if not chunks:
        raise ValueError("Không trích xuất được nội dung.")
    insert_chunks(doc_id, chunks)
    os.remove(temp_path)
    return {"doc_id": doc_id, "chunks": len(chunks)}

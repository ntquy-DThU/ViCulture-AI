import numpy as np
from sentence_transformers import SentenceTransformer
from app.db import run_sql

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_model = None

def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_texts(texts):
    model = get_embedder()
    embs = model.encode(texts, normalize_embeddings=True)
    return np.asarray(embs, dtype=np.float32)

def insert_document(filename, content_type):
    row = run_sql(
        "INSERT INTO documents(filename, content_type) VALUES (:f,:c) RETURNING id",
        f=filename, c=content_type
    ).first()
    return int(row[0])

def insert_chunks(doc_id, items):
    texts = [t for t, _ in items]
    embs = embed_texts(texts)
    for (text, page), emb in zip(items, embs):
        run_sql(
            "INSERT INTO chunks(doc_id, page, text, embedding) VALUES (:d, :p, :t, :e)",
            d=doc_id, p=page, t=text, e=list(emb)
        )

def search_similar(question: str, top_k=3):
    q_emb = embed_texts([question])[0].tolist()
    rows = run_sql("""
        SELECT d.filename, c.page, c.text,
               1 - (c.embedding <=> :q::vector) AS score
        FROM chunks c
        JOIN documents d ON d.id = c.doc_id
        ORDER BY c.embedding <=> :q::vector
        LIMIT :k
    """, q=q_emb, k=top_k).fetchall()
    return [{"filename": fn, "page": page, "text": txt.strip(), "score": float(score)}
            for fn, page, txt, score in rows]

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  content_type TEXT,
  uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
  id SERIAL PRIMARY KEY,
  doc_id INT REFERENCES documents(id) ON DELETE CASCADE,
  page INT,
  text TEXT NOT NULL,
  embedding VECTOR(384) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding
  ON chunks
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

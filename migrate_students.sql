CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  fullname TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  student_code TEXT,
  password_hash TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMP DEFAULT NOW()
);

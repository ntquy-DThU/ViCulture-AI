import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

PG_URL = os.getenv("DATABASE_URL")  # Render cung cấp

engine = create_engine(
    PG_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
def run_sql(sql, **params):
    with engine.begin() as conn:
        return conn.execute(text(sql), params)

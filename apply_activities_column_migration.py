"""Apply alter_activities_term_columns.sql to the database."""
from pathlib import Path

from sqlalchemy import text

from app.db.database import engine

sql_path = Path(__file__).resolve().parent / "alter_activities_term_columns.sql"
raw = sql_path.read_text(encoding="utf-8")
statements = [
    s.strip()
    for s in raw.split(";")
    if s.strip() and not all(line.strip().startswith("--") or not line.strip() for line in s.splitlines())
]

with engine.begin() as conn:
    for stmt in statements:
        if stmt:
            conn.execute(text(stmt))

print("Migration applied: activities term columns -> TEXT")

with engine.connect() as conn:
    row = conn.execute(
        text("SHOW COLUMNS FROM activities WHERE Field = 'short_term'")
    ).fetchone()
    print("short_term column type:", row[1] if row else "unknown")

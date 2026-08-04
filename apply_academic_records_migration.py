"""Apply alter_academic_records.sql using DATABASE_URL from .env."""
import os
import re
from urllib.parse import unquote

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pymysql

sql_path = os.path.join(os.path.dirname(__file__), "alter_academic_records.sql")
with open(sql_path, encoding="utf-8") as f:
    content = f.read()

statements = []
for raw in content.split(";"):
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        lines.append(line)
    stmt = "\n".join(lines).strip()
    if stmt:
        statements.append(stmt)

url = os.getenv("DATABASE_URL", "")
match = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)", url)
if not match:
    raise SystemExit("DATABASE_URL not set or invalid")
user, password, host, port, database = match.groups()
password = unquote(password)
database = database.split("?")[0]

conn = pymysql.connect(host=host, port=int(port), user=user, password=password, database=database)
cur = conn.cursor()
for stmt in statements:
    try:
        cur.execute(stmt)
        print(f"OK: {stmt[:80]}...")
    except Exception as exc:
        msg = str(exc).lower()
        if "duplicate column" in msg or "duplicate key name" in msg or "already exists" in msg:
            print(f"SKIP (already applied): {stmt[:60]}...")
        else:
            raise
conn.commit()
print("Academic records migration applied.")
conn.close()

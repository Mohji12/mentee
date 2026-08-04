"""Apply add_dashboard_enhancement_tables.sql using DATABASE_URL from .env."""
import os
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pymysql

sql_path = os.path.join(os.path.dirname(__file__), "add_dashboard_enhancement_tables.sql")
with open(sql_path, encoding="utf-8") as f:
    content = f.read()

statements = [s.strip() for s in content.split(";") if s.strip() and not s.strip().startswith("--")]

url = os.getenv("DATABASE_URL", "")
# mysql+pymysql://user:pass@host:port/db
match = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)", url)
if not match:
    raise SystemExit("DATABASE_URL not set or invalid")
user, password, host, port, database = match.groups()
from urllib.parse import unquote
password = unquote(password)
database = database.split("?")[0]

conn = pymysql.connect(host=host, port=int(port), user=user, password=password, database=database)
cur = conn.cursor()
for stmt in statements:
    cur.execute(stmt)
conn.commit()
print("Dashboard enhancement tables migration applied.")
conn.close()

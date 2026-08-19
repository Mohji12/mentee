"""Export entire MySQL database: CREATE TABLE + INSERT data."""
import os
import re
from datetime import date, datetime, time
from decimal import Decimal
from urllib.parse import unquote

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pymysql

url = os.getenv("DATABASE_URL", "")
match = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)", url)
if not match:
    raise SystemExit("DATABASE_URL not set or invalid")

user, password, host, port, database = match.groups()
password = unquote(password)
database = database.split("?")[0]
port = int(port)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{database}_full_dump.sql")
BATCH = 500


def sql_literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    if isinstance(value, datetime):
        return "'" + value.strftime("%Y-%m-%d %H:%M:%S") + "'"
    if isinstance(value, date):
        return "'" + value.strftime("%Y-%m-%d") + "'"
    if isinstance(value, time):
        return "'" + value.strftime("%H:%M:%S") + "'"
    if isinstance(value, bytes):
        return "0x" + value.hex()
    text = str(value).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
    return "'" + text + "'"


conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.Cursor,
)
cur = conn.cursor()
cur.execute("SHOW TABLES")
tables = [row[0] for row in cur.fetchall()]

with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(f"-- Full dump of `{database}`\n")
    f.write(f"-- Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    f.write("SET NAMES utf8mb4;\n")
    f.write("SET FOREIGN_KEY_CHECKS=0;\n")
    f.write("SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO';\n\n")

    for table in tables:
        print(f"Dumping {table}...")
        f.write(f"-- --------------------------------------------------------\n")
        f.write(f"-- Table `{table}`\n")
        f.write(f"-- --------------------------------------------------------\n")
        f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
        cur.execute(f"SHOW CREATE TABLE `{table}`")
        create_sql = cur.fetchone()[1]
        f.write(create_sql + ";\n\n")

        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        total = cur.fetchone()[0]
        if total == 0:
            f.write(f"-- `{table}` has no rows\n\n")
            continue

        offset = 0
        while offset < total:
            cur.execute(f"SELECT * FROM `{table}` LIMIT {BATCH} OFFSET {offset}")
            rows = cur.fetchall()
            if not rows:
                break
            cols = [d[0] for d in cur.description]
            col_sql = ", ".join(f"`{c}`" for c in cols)
            values = []
            for row in rows:
                values.append("(" + ", ".join(sql_literal(v) for v in row) + ")")
            f.write(f"INSERT INTO `{table}` ({col_sql}) VALUES\n")
            f.write(",\n".join(values))
            f.write(";\n\n")
            offset += BATCH
            print(f"  {min(offset, total)}/{total} rows")

    f.write("SET FOREIGN_KEY_CHECKS=1;\n")

cur.close()
conn.close()
print(f"Wrote {out_path}")

import pymysql
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

print("Applying schema to skillswap_test on port 3306...")
conn = pymysql.connect(host="127.0.0.1", port=3306, user="skillswap", password="skillswap_pass", database="skillswap_test", autocommit=True)

schema_path = "backend/database/schema.sql" if os.path.exists("backend/database/schema.sql") else "database/schema.sql"
with open(schema_path, "r", encoding="utf-8") as f:
    sql_content = f.read()

with conn.cursor() as cur:
    for stmt in sql_content.split(";"):
        cleaned = stmt.strip()
        lines = [l for l in cleaned.splitlines() if not l.strip().startswith("--")]
        if lines and "".join(lines).strip():
            cur.execute(cleaned)

print("schema.sql applied successfully to skillswap_test!")

with conn.cursor() as cur:
    cur.execute("SHOW TABLES;")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables in skillswap_test:", tables)

conn.close()


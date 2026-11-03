import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host="127.0.0.1", port=3306, user="skillswap", password="skillswap_pass", database="skillswap", autocommit=True)

with open("backend/database/test_queries.sql", "r", encoding="utf-8") as f:
    sql_text = f.read()

# Split statements by semicolon while ignoring comments
raw_statements = sql_text.split(";")
queries_executed = 0
errors = []

with conn.cursor() as cur:
    for stmt in raw_statements:
        cleaned = stmt.strip()
        lines = [l for l in cleaned.splitlines() if not l.strip().startswith("--")]
        code = "\n".join(lines).strip()
        if not code:
            continue
        try:
            cur.execute(code)
            queries_executed += 1
            # If it's a SELECT, fetch rows
            if cur.description:
                rows = cur.fetchall()
                # print first query preview
                first_line = [l for l in cleaned.splitlines() if l.strip() and not l.strip().startswith("--")][0]
                # print(f"OK ({len(rows)} rows): {first_line[:60]}")
        except Exception as e:
            errors.append((cleaned[:100], str(e)))

conn.close()

print(f"\nTotal statements executed: {queries_executed}")
print(f"Errors encountered: {len(errors)}")
for q, err in errors:
    print(f"\nERROR in:\n{q}\n--> {err}")


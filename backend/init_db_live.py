import pymysql
import re

print("Connecting to MySQL on 127.0.0.1:3306 as root...")
conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Hansika@2008", autocommit=True)

with conn.cursor() as cur:
    print("1. Creating databases skillswap and skillswap_test...")
    cur.execute("CREATE DATABASE IF NOT EXISTS skillswap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cur.execute("CREATE DATABASE IF NOT EXISTS skillswap_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    print("2. Configuring user skillswap...")
    try:
        cur.execute("CREATE USER IF NOT EXISTS 'skillswap'@'localhost' IDENTIFIED BY 'skillswap_pass';")
    except Exception as e:
        print("Note on create user localhost:", e)
    try:
        cur.execute("CREATE USER IF NOT EXISTS 'skillswap'@'%' IDENTIFIED BY 'skillswap_pass';")
    except Exception as e:
        print("Note on create user %:", e)
        
    cur.execute("GRANT ALL PRIVILEGES ON skillswap.* TO 'skillswap'@'localhost';")
    cur.execute("GRANT ALL PRIVILEGES ON skillswap.* TO 'skillswap'@'%';")
    cur.execute("GRANT ALL PRIVILEGES ON skillswap_test.* TO 'skillswap'@'localhost';")
    cur.execute("GRANT ALL PRIVILEGES ON skillswap_test.* TO 'skillswap'@'%';")
    cur.execute("FLUSH PRIVILEGES;")
    print("User and databases configured!")

conn.close()

# Now connect directly to skillswap
print("3. Connecting to skillswap database to execute schema.sql...")
conn_db = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Hansika@2008", database="skillswap", autocommit=True)

def execute_sql_file(filepath, connection):
    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split statements by semicolon while ignoring comments
    statements = []
    # Simple statement splitter that handles multiline
    raw_statements = sql_content.split(";")
    for stmt in raw_statements:
        cleaned = stmt.strip()
        if cleaned:
            # Check if it has actual code, not just comment lines
            lines = [l for l in cleaned.splitlines() if not l.strip().startswith("--")]
            if lines and "".join(lines).strip():
                statements.append(cleaned)

    with connection.cursor() as cur:
        for stmt in statements:
            try:
                cur.execute(stmt)
            except Exception as e:
                print(f"Error on statement:\n{stmt[:100]}...\n-> {e}")
                raise e

print("Executing schema.sql...")
execute_sql_file("database/schema.sql", conn_db)
print("schema.sql executed successfully!")

print("4. Executing seed.sql...")
execute_sql_file("database/seed.sql", conn_db)
print("seed.sql executed successfully!")

# Verify table counts
with conn_db.cursor() as cur:
    cur.execute("SHOW TABLES;")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables in skillswap:", tables)
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM `{t}`;")
        cnt = cur.fetchone()[0]
        print(f"  {t}: {cnt} rows")

conn_db.close()
print("ALL SETUP COMPLETE!")

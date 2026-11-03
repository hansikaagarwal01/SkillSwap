import sys
import re
import argparse
from urllib.parse import urlparse
import pymysql
from app.core.config import settings

sys.stdout.reconfigure(encoding="utf-8")


def parse_db_url(url: str):
    # e.g. mysql+pymysql://skillswap:pass@127.0.0.1:3306/skillswap_test?charset=utf8mb4
    cleaned = url.replace("mysql+pymysql://", "mysql://")
    parsed = urlparse(cleaned)
    db_name = parsed.path.lstrip("/").split("?")[0]
    return {
        "host": parsed.hostname or "127.0.0.1",
        "port": parsed.port or 3306,
        "user": parsed.username or "skillswap",
        "password": parsed.password or "",
        "database": db_name,
    }


def split_sql_statements(sql_text: str):
    """
    Cleans comments and splits SQL statements by semicolon,
    preserving strings and block comments.
    """
    # Remove block comments /* ... */
    sql_clean = re.sub(r"/\*.*?\*/", "", sql_text, flags=re.DOTALL)
    
    statements = []
    current = []
    in_string = False
    quote_char = None

    for line in sql_clean.splitlines():
        line_stripped = line.strip()
        # Skip single-line comments
        if not in_string and line_stripped.startswith("--"):
            continue

        for i, ch in enumerate(line):
            if ch in ("'", '"', '`') and (i == 0 or line[i - 1] != "\\"):
                if not in_string:
                    in_string = True
                    quote_char = ch
                elif quote_char == ch:
                    in_string = False
                    quote_char = None
            elif ch == ";" and not in_string:
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                continue
            current.append(ch)
        current.append("\n")

    remainder = "".join(current).strip()
    if remainder:
        statements.append(remainder)

    return statements


def main():
    parser = argparse.ArgumentParser(description="SkillSwap JKLU SQL Test Query Verifier")
    parser.add_argument("--live", action="store_true", help="Run against primary database instead of test database")
    args = parser.parse_args()

    db_url = settings.DATABASE_URL if args.live else settings.TEST_DATABASE_URL
    conn_params = parse_db_url(db_url)

    target_name = conn_params["database"]
    print(f"============================================================")
    print(f"SkillSwap JKLU — Executing Demonstration SQL Queries")
    print(f"Target Database: {target_name} ({conn_params['host']}:{conn_params['port']})")
    print(f"============================================================")

    conn = pymysql.connect(
        host=conn_params["host"],
        port=conn_params["port"],
        user=conn_params["user"],
        password=conn_params["password"],
        database=conn_params["database"],
        charset="utf8mb4",
        autocommit=False,  # Essential for Query 2 ACID rollback verification
    )

    with open("backend/database/test_queries.sql", "r", encoding="utf-8") as f:
        sql_text = f.read()

    statements = split_sql_statements(sql_text)
    executed = 0
    errors = []

    with conn.cursor() as cur:
        for stmt in statements:
            # Strip initial USE database if testing against test db
            if stmt.upper().startswith("USE "):
                if not args.live:
                    continue  # Keep connection to test db

            try:
                cur.execute(stmt)
                executed += 1
                if cur.description:
                    cur.fetchall()
            except Exception as exc:
                errors.append((stmt, str(exc)))

    conn.close()

    print(f"Total SQL Statements Evaluated: {executed}")
    print(f"Errors Encountered: {len(errors)}")

    if errors:
        print("\nFAILURES:")
        for sql_part, err_msg in errors:
            print("------------------------------------------------------------")
            print(f"Query:\n{sql_part[:180]}...")
            print(f"Error: {err_msg}")
        sys.exit(1)
    else:
        print("\nAll SQL demonstration queries successfully PASSED with 0 errors!")
        sys.exit(0)


if __name__ == "__main__":
    main()

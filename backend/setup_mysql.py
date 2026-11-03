import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Connecting as root to MySQL on 127.0.0.1:3306...")
conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Hansika@2008", autocommit=True)
with conn.cursor() as cur:
    print("1. Creating databases skillswap and skillswap_test...")
    cur.execute("CREATE DATABASE IF NOT EXISTS skillswap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cur.execute("CREATE DATABASE IF NOT EXISTS skillswap_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    print("2. Configuring user skillswap...")
    cur.execute("CREATE USER IF NOT EXISTS 'skillswap'@'localhost' IDENTIFIED BY 'skillswap_pass';")
    cur.execute("ALTER USER 'skillswap'@'localhost' IDENTIFIED BY 'skillswap_pass';")
    cur.execute("CREATE USER IF NOT EXISTS 'skillswap'@'%' IDENTIFIED BY 'skillswap_pass';")
    cur.execute("ALTER USER 'skillswap'@'%' IDENTIFIED BY 'skillswap_pass';")
    
    cur.execute("GRANT ALL PRIVILEGES ON skillswap.* TO 'skillswap'@'localhost';")
    cur.execute("GRANT ALL PRIVILEGES ON skillswap.* TO 'skillswap'@'%';")
    cur.execute("GRANT ALL PRIVILEGES ON skillswap_test.* TO 'skillswap'@'localhost';")
    cur.execute("GRANT ALL PRIVILEGES ON skillswap_test.* TO 'skillswap'@'%';")
    cur.execute("FLUSH PRIVILEGES;")
    print("User and privileges configured!")
conn.close()

# Test connection
print("3. Testing connection as skillswap user...")
test_conn = pymysql.connect(host="127.0.0.1", port=3306, user="skillswap", password="skillswap_pass", database="skillswap")
print("SUCCESS: Connected as skillswap user on port 3306 to database skillswap!")
test_conn.close()


from db import get_db_connection

try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT version();')
    db_version = cur.fetchone()
    print("✅ Connection successful!")
    print("PostgreSQL version:", db_version)

    cur.close()
    conn.close()
except Exception as e:
    print("❌ Connection failed!")
    print(e)

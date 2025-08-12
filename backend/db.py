import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="medical_assistant1",
        user="super_user",
        password="jm32"
    )
    return conn

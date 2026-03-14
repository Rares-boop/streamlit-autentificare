import re

import bcrypt
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_DATABASE")

def get_connection():
    return psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    if password is None:
        return None
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def is_email_valid(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def email_check(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM USERS WHERE email = %s",(email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(full_name, email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO USERS (full_name, email, password_hash) VALUES (%s, %s, %s)"
            " RETURNING id, full_name",
            (full_name, email, password_hash)
        )
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        return result[0], result[1]
    except Exception as e:
        return None

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, password_hash FROM USERS WHERE email = %s", (email,))
    result = cursor.fetchone()
    conn.close()
    if result and result[2]:
        if bcrypt.checkpw(password.encode(), result[2].encode()):
            return result[0], result[1]

    return None

def login_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name FROM USERS WHERE email = %s",(email,))
    result = cursor.fetchone()
    conn.close()
    return result



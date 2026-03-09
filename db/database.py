import re
import sqlite3
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(32).hex()
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt

def is_email_valid(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def email_check(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM USERS WHERE email = ?",(email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(full_name, email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash, salt = hash_password(password)
        cursor.execute(
            "INSERT INTO USERS (full_name, email, password_hash, salt) VALUES (?, ?, ?, ?)"
            " RETURNING id, full_name",
            (full_name, email, password_hash, salt)
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
    cursor.execute("SELECT id, full_name, password_hash, salt FROM USERS WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    if result:
        password_hash, _ = hash_password(password, result[3])
        if password_hash == result[2]:
            return result[0], result[1]
    return None


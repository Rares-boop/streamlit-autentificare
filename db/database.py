import bcrypt
import psycopg2
import os
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
import secrets

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
            confirmation_token TEXT,
            confirmed BOOLEAN DEFAULT FALSE,
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
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

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
        confirmation_token = secrets.token_urlsafe(32)
        cursor.execute(
            "INSERT INTO USERS (full_name, email, password_hash, confirmation_token) VALUES (%s, %s, %s, %s)"
            " RETURNING id, full_name",
            (full_name, email, password_hash, confirmation_token)
        )
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        return result[0], result[1], confirmation_token
    except Exception as e:
        return None

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, password_hash, confirmed FROM USERS WHERE email = %s", (email,))
    result = cursor.fetchone()
    conn.close()
    if result and result[2]:

        if bcrypt.checkpw(password.encode(), result[2].encode()):
            if not result[3]:
                return None, "unconfirmed"
            return result[0], result[1]
    return None, None

def register_user_google(full_name, email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO USERS (full_name, email, confirmed) VALUES (%s, %s, TRUE)"
            " RETURNING id, full_name",
            (full_name, email)
        )
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        return result[0], result[1]
    except Exception as e:
        return None

def login_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name FROM USERS WHERE email = %s",(email,))
    result = cursor.fetchone()
    conn.close()
    return result

def check_google_login(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, password_hash FROM USERS WHERE email = %s",(email,))
    result = cursor.fetchone()
    conn.close()
    return result

def check_confirmation_token(confirmation_token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM USERS WHERE confirmation_token = %s AND confirmed = FALSE", (confirmation_token,))
    result = cursor.fetchone()
    conn.close()
    return result

def confirm_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE USERS SET confirmed = TRUE, confirmation_token = NULL WHERE id = %s",
            (user_id,)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False


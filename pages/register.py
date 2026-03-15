import time

import streamlit as st
from streamlit_cookies_controller import CookieController

from auth.jwt_utils import check_token
from db.database import email_check, is_email_valid, register_user

from auth.email_utils import send_confirmation_email

st.set_page_config(page_title="Register", layout="centered")

controller = CookieController()
token = controller.get("token")

if token and check_token(token):
    st.switch_page("home.py")

st.title("📝 Register")

full_name = st.text_input("Full Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
password_confirm = st.text_input("Confirm Password", type="password")

if st.button("Register"):
    if not full_name or not email or not password or not password_confirm:
        st.warning("Please fill in all fields.")
    elif not is_email_valid(email):
        st.error("Invalid email address.")
    elif len(password) < 6:
        st.error("Password must be at least 6 characters.")
    elif password != password_confirm:
        st.error("Passwords do not match.")
    elif email_check(email):
        st.error("An account with this email already exists.")
    else:
        result = register_user(full_name, email, password)
        if result is not None:
            send_confirmation_email(email, result[2])
            st.success("Account created! Please check your email to confirm your account.")
            time.sleep(5)
            st.switch_page("pages/login.py")
        else:
            st.error("Something went wrong. Please try again.")

if st.button("Already have an account? Login"):
    st.switch_page("pages/login.py")

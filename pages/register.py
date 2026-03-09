import streamlit as st
from streamlit_cookies_controller import CookieController

from auth.jwt_utils import generate_token
from db.database import email_check, is_email_valid, register_user

controller = CookieController()

st.set_page_config(page_title="Register", layout="centered")
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
            st.success(f"Account created successfully! Welcome, {result[1]}!")
            token = generate_token(result[0], email)
            controller.set("token", token)
            st.success("Login successful")
            st.switch_page("home.py")
        else:
            st.error("Something went wrong. Please try again.")

if st.button("Already have an account? Login"):
    st.switch_page("pages/login.py")

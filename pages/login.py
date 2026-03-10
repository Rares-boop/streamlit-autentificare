import streamlit as st
from streamlit_cookies_controller import CookieController
from auth.jwt_utils import generate_token, check_token
from db.database import login_user

st.set_page_config(page_title="Login", layout="centered")

controller = CookieController()
token = controller.get("token")

if token and check_token(token):
    st.switch_page("home.py")

st.title("🔐 Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not email or not password:
        st.warning("Complete the login")
    else:
        result = login_user(email, password)
        if result:
            token = generate_token(result[0], email)
            controller.set("token", token)
            st.success("Login successful")
            st.switch_page("home.py")
        else:
            st.error("Email or password incorrect")

if st.button("Register here"):
    st.switch_page("pages/register.py")


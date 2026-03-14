import streamlit as st
from streamlit_cookies_controller import CookieController
from auth.jwt_utils import generate_token, check_token
from db.database import login_user, email_check, register_user, login_user_by_email
import time

st.set_page_config(page_title="Login", layout="centered")

controller = CookieController()
token = controller.get("token")

if token and check_token(token):
    st.switch_page("home.py")

if st.user.is_logged_in:
    if not email_check(st.user.email):
        register_user(st.user.name, st.user.email, None)
    user_id, _ = login_user_by_email(st.user.email)
    token = generate_token(user_id, st.user.email)
    controller.set("token", token)
    st.switch_page("home.py")

st.title("🔐 Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0
    st.session_state.lockout_time = 0

if st.button("Login"):
    if time.time() < st.session_state.lockout_time:
        remaining = int(st.session_state.lockout_time - time.time())
        st.error(f"Too many attempts. Try again in {remaining} seconds.")
    elif not email or not password:
        st.warning("Complete the login")
    else:
        result = login_user(email, password)
        if result:
            st.session_state.login_attempts = 0
            token = generate_token(result[0], email)
            controller.set("token", token)
            st.switch_page("home.py")
        else:
            st.session_state.login_attempts += 1
            if st.session_state.login_attempts >= 5:
                st.session_state.lockout_time = time.time() + 60
                st.error("Too many attempts. Locked for 60 seconds.")
            else:
                st.error(f"Email or password incorrect. ({st.session_state.login_attempts}/5)")

st.divider()
st.button("Login with Google", on_click=st.login, args=("google",))

if st.button("Register here"):
    st.switch_page("pages/register.py")


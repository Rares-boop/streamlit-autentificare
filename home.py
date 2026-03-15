import streamlit as st
from streamlit_cookies_controller import CookieController
from auth.jwt_utils import check_token
from db.database import check_google_login

st.set_page_config(page_title="Home", layout="centered")

controller = CookieController()
token = controller.get("token")

payload = check_token(token)

if not token or not payload:
    st.switch_page("pages/login.py")

email = payload.get("email")
result = check_google_login(email)

full_name = result[0]
login_method = "Google" if result[1] is None else "Email & Password"

st.title("Home page")
st.write("This is the home page")

st.write(f"Welcome, **{full_name}**!")
st.write(f"Logged in with: **{login_method}**")

if st.button("Logout"):
    controller.remove("token")
    st.logout()


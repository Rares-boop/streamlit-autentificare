import streamlit as st
from streamlit_cookies_controller import CookieController
from auth.jwt_utils import check_token

st.set_page_config(page_title="Home", layout="centered")

controller = CookieController()
token = controller.get("token")

if not token or not check_token(token):
    st.switch_page("pages/login.py")

st.title("Home page")
st.write("This is the home page")

if st.button("Logout"):
    controller.remove("token")
    st.logout()


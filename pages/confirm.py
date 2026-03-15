import streamlit as st
from db.database import check_confirmation_token, confirm_user
import time

st.set_page_config(page_title="Confirm Account", layout="centered")

token = st.query_params.get("token")

if not token:
    st.error("Invalid confirmation link.")
    st.stop()

result = check_confirmation_token(token)

if result:
    success = confirm_user(result[0])
    if success:
        st.success("Account confirmed! You can now login.")
        time.sleep(2)
        st.switch_page("pages/login.py")
    else:
        st.error("Something went wrong. Please try again.")
else:
    st.error("Invalid or already used confirmation link.")




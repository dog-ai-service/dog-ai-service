from services.login_api import login_api
# ui
import streamlit as st

def user_page():
    if "token" not in st.session_state:
        st.title("로그인 해주세요")
    else:
        st.title("유저 개인정보창")
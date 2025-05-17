from services.login_api import login_api
# ui
import streamlit as st
#사이드바 로그인
from components.sidebar import sidebar
sidebar()

if "token" not in st.session_state:
    st.title("로그인 해주세요")
else:
    st.title("유저 개인정보창")
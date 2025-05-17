# ui
import streamlit as st
from services.login_api import login_api

#사이드바
def sidebar():
    with st.sidebar:
        login_api()
    choice = st.sidebar.radio("페이지 선택", ["캘린더", "챗봇", "사용자 정보"])
    return choice
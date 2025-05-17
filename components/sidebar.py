# ui
import streamlit as st
from services.login_api import login_api

#사이드바
def sidebar():
    with st.sidebar:
        with st.container():
            st.markdown('<div style="border:1px solid #ccc; padding:10px; border-radius:5px;">', unsafe_allow_html=True)
            
            login_api()

            st.markdown('</div>', unsafe_allow_html=True)
    choice = st.sidebar.radio("페이지 선택", ["캘린더", "챗봇", "사용자 정보"])
    return choice
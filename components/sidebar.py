# ui
import streamlit as st

#사이드바
def sidebar():
    st.sidebar.title('this is sidebar')
    choice = st.sidebar.radio("페이지 선택", ["캘린더", "챗봇", "사용자 정보"])
    return choice

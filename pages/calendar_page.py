# ui
import streamlit as st
from services.calendar_api import session_calendar_id
# streamlit 캘린더 ui
from components.st_calendar import st_calendar
#사이드바 로그인
from components.sidebar import sidebar
sidebar()
# 셀렉트에 따라 캘린더 키 값 받아오기
if "token" in st.session_state:
    session_calendar_id()
st_calendar()

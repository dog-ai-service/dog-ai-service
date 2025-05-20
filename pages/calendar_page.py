# ui
import streamlit as st
# streamlit 캘린더 ui
from components.st_calendar import st_calendar
#사이드바 로그인
from components.sidebar import sidebar
# 일정 생성 및 일정 요약
from components.create_schedule import create_schedule
sidebar()
st_calendar()
create_schedule()

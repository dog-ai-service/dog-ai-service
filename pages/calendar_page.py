# ui
import streamlit as st
# 구글 캘린더 api
from services.calendar_api import calendar_api
# 구글 테스크 api
from services.tasks_api import tasks_api
# streamlit 캘린더 ui
from components.st_calendar import st_calendar
#사이드바 로그인
from components.sidebar import sidebar
# 일정 생성 및 일정 요약
from components.create_schedule import create_schedule
sidebar()
st_calendar()
create_schedule()

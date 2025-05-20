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
sidebar()
st.info({'kind': 'calendar#events', 'etag': '"p337s9gskl6o8q0o"', 'summary': 'mlstudy213@gmail.com', 'description': '', 'updated': '2025-05-19T19:59:41.253Z', 'timeZone': 'Asia/Seoul', 'accessRole': 'owner', 'defaultReminders': [{'method': 'popup', 'minutes': 30}], 'items': []})
st_calendar()

# ui
import streamlit as st
# 사이드바 로그인
from components.sidebar import sidebar
#
from services.drive_api import sheet_create, sheet_write, sheet_read
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

sidebar()

client_id=GOOGLE_CLIENT_ID
client_secret=GOOGLE_CLIENT_SECRET

if "token" in st.session_state:
    # 캘린더 목록 가져오기
    token = st.session_state.token
        # 캘린더에 사용을 위한 구글계정 정보를 세션에서 가져오기
    creds = Credentials(
        token=token["token"]["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    # 캘린더 API 서비스 객체 생성
    service = build("calendar", "v3", credentials=creds)
    calendar_list = service.calendarList().list().execute()

    # 각 캘린더 출력
    for calendar_entry in calendar_list.get("items", []):
        st.info(f"캘린더 이름:{calendar_entry.get("summary","없음")}\n")
        st.info(f"캘린더 ID: {calendar_entry.get("id","없음")}")
        st.info(f"소유권:{calendar_entry.get("accessRole","없음")}")
# ui
import streamlit as st
# 구글 캘린더 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET



def calendar_api():
    client_id=GOOGLE_CLIENT_ID
    client_secret=GOOGLE_CLIENT_SECRET

    # 세션 상태에 token이 없으면 로그인 버튼 표시
    # 사용할 계정의 Google Calendar API를 사용 상태로 바꾸어야 사용가능
    if "token" not in st.session_state:
        st.title("로그인 안됨")
    else:
        token = st.session_state.token
        # 캘린더에 사용을 위한 구글계정 정보를 세션에서 가져오기
        creds = Credentials(
            token=token["token"]["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/tasks"]
        )
        # 구글 테스크 API 서비스 객체 생성
        service = build("tasks", "v1", credentials=creds)
        # 2020년부터 가져오기
        time_min = "2020-01-01T00:00:00Z"
        # 2020년부터 가져오기
        time_max = "2030-01-01T00:00:00Z"
        # 구글 테스크에서 대충 최신 이벤트 50개 가져오기
        tasks_result = service.tasks().list(
            tasklist='@default',
            maxResults=50,
            showCompleted=True,
            showDeleted=False,
            dueMin='2020-01-01T00:00:00Z',
            dueMax='2025-12-31T23:59:59Z'
        ).execute()
        events = tasks_result.get("items", [])
        st.write(events)

        return





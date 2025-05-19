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
        # 구글 테스크에 사용을 위한 구글계정 정보를 세션에서 가져오기
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
        # 오늘 일정 가져오기
        time_min = "2000-01-01T00:00:00Z"
        # 캘린더에서 대충 최신 이벤트 5개 가져오기
        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        st.write(events)

        calendar_events=[]

        st.subheader("📅 오늘 이후 이벤트")
        if not events:
            st.write("예정된 일정이 없습니다.")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            st.write(f"- {start}: {event['summary']}")
            
            is_datetime = "dateTime" in event["start"]

            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event.get("end", {}).get("dateTime", None)  # end는 없을 수도 있음

            event_data = {
                "title": event["summary"],
                "start": start[:16] if is_datetime else start,
                "resourceId": "a",
            }

            if is_datetime:
                event_data["end"] = end[:16] if end else start[:16]
                event_data["allDay"] = False
            else:
                event_data["allDay"] = True

            calendar_events.append(event_data)
        return calendar_events





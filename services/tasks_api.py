# ui
import streamlit as st
# 구글 캘린더 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET



def tasks_api():
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
            dueMin=time_min,
            dueMax=time_max
        ).execute()
        events = tasks_result.get("items", [])

        tasks_events=list()

        st.subheader("📅 오늘 이후 이벤트")
        if not events:
            st.write("예정된 일정이 없습니다.")
        for event in events:
            is_summary = "title" in event
            is_completed=True if event["status"]=="completed" else False
            
            # 완료된 일정
            if is_completed:
                continue

            date=event["due"]

            event_data = {
                "title": "Task : "+(event['title'] if is_summary else "제목없음"),
                "start": date[:10],
                "resourceId": "a",
                "allDay" : True,
            }
            tasks_events.append(event_data)
        return tasks_events

'''
json 형식
https://developers.google.com/workspace/tasks/reference/rest/v1/tasks?hl=ko

{
  "kind": string,
  "id": string,
  "etag": string,
  "title": string,
  "updated": string,
  "selfLink": string,
  "parent": string,
  "position": string,
  "notes": string,
  "status": string,
  "due": string,
  "completed": string,
  "deleted": boolean,
  "hidden": boolean,
  "links": [
    {
      "type": string,
      "description": string,
      "link": string
    }
  ],
  "webViewLink": string,
  "assignmentInfo": {
    object (AssignmentInfo)
  }
}

'''



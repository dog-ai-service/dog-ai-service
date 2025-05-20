# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from services.make_creds_api import make_creds



def tasks_api():
    creds = make_creds("tasks")
    if creds:
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



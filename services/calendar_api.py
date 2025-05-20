# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from services.make_creds_api import make_creds
# 설정값
from config import TIME_MIN,TIME_MAX,MAX_RESULTS


# 구글 캘린더 서비스
def calendar_service():
    client_id=GOOGLE_CLIENT_ID
    client_secret=GOOGLE_CLIENT_SECRET

    # 세션 상태에 token이 없으면 로그인 버튼 표시
    # 사용할 계정의 Google Calendar API를 사용 상태로 바꾸어야 사용가능
    if "token" not in st.session_state:
        return None
    else:
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
    
    return service

def calendar_api():
    creds = make_creds("calendar")
    if creds:
        # 캘린더 API 서비스 객체 생성
        service = build("calendar", "v3", credentials=creds)
    # TIME_MIN년부터 가져오기
    time_min = TIME_MIN
    # TIME_MAX년까지 가져오기
    time_max = TIME_MAX
    # 캘린더에서 대충 최신 이벤트 50개 가져오기
    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        maxResults=MAX_RESULTS,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    calendar_events=[]

    if not events:
        st.write("예정된 일정이 없습니다.")
    for event in events:
        is_datetime = "dateTime" in event["start"]
        is_summary = "summary" in event

        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event.get("end", {}).get("dateTime", None)  # end는 없을 수도 있음

        event_data = {
            "title": event['summary'] if is_summary else "제목없음",
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

# calendar_id의 캘린더 이벤트를 리스트(딕셔너리) 형태로 반환
def get_calendar_events(calendar_id):
    service=calendar_service()
    # 미로그인 시 값없음
    if service is None:
        return []

    # 2020년부터 가져오기
    time_min = TIME_MIN
    # 2020년부터 가져오기
    time_max = TIME_MAX
    # 캘린더에서 대충 최신 이벤트 50개 가져오기
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        maxResults=MAX_RESULTS,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    calendar_events=[]

    if not events:
        st.write("예정된 일정이 없습니다.")
    for event in events:
        is_datetime = "dateTime" in event["start"]
        is_summary = "summary" in event

        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event.get("end", {}).get("dateTime", None)  # end는 없을 수도 있음

        event_data = {
            "title": event['summary'] if is_summary else "제목없음",
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

# 세션.selected_calendar에 모든 캘린더 목록의 정보 저장 딕(id, summary)
def session_set_calendar_list():
    service=calendar_service()
    if service is None:
        print("로그인 안됨")
        return 
    calendar_list={}
    # 캘린더 목록 전부 가져오기
    page_token = None
    while True:
        calendar_list_origin = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list_origin['items']:
            # 캘린더 목록을 딕셔너리에 (id, summary)로 추가
            calendar_list[calendar_list_entry["id"]]=calendar_list_entry['summary'] 
        page_token = calendar_list_origin.get('nextPageToken')
        if not page_token:
            break
    st.session_state.calendar_list = calendar_list


    


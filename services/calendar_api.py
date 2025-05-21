# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from services.make_creds_api import make_creds
# 설정값
from config import TIME_MIN,TIME_MAX,MAX_RESULTS

# calendar_id의 캘린더 이벤트를 리스트(딕셔너리) 형태로 반환 / 미로그인시 []로 널값 반환
def get_calendar_events(calendar_id):
    creds = make_creds("calendar")
    
    # 미로그인시 [] 반환
    if not creds:
        st.error("❌ 먼저 로그인하세요")
        return []

    # 캘린더 API 서비스 객체 생성
    service = build("calendar", "v3", credentials=creds)

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
            "description" : event.get("description", "설명없음"),
            "calendar_id" : calendar_id,
            "calendar_summary" : st.session_state.calendar_list.get(calendar_id, "제목없음")
        }

        if is_datetime:
            event_data["end"] = end[:16] if end else start[:16]
            event_data["allDay"] = False
        else:
            event_data["allDay"] = True

        calendar_events.append(event_data)
    return calendar_events

# 세션.selected_calendar에 모든 캘린더 목록의 정보 저장 딕(id, summary) / 실패 시 
def session_set_calendar_list():
    creds = make_creds("calendar")
    
    # 미로그인시 [] 반환
    if not creds:
        st.error("❌ 먼저 로그인하세요")
        return

    # 캘린더 API 서비스 객체 생성
    service = build("calendar", "v3", credentials=creds)
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


def get_calendar_service():
    """
    세션의 OAuth 토큰으로 Google Calendar API 서비스 객체를 생성해 리턴합니다.
    """
    if "token" not in st.session_state:
        st.error("Google 로그인 정보가 없습니다.")
        return None

    tok = st.session_state.token
    # 토큰 키 이름은 실제 저장 구조에 맞춰 조정하세요
    access_token  = tok.get("access_token") or tok["token"]["access_token"]
    refresh_token = tok.get("refresh_token")

    creds = make_creds("calendar")
    
    # 미로그인시 fl
    if not creds:
        st.error("Google 로그인 정보가 없습니다.")
        return
    
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        st.error(f"캘린더 서비스 생성 오류: {e}")
        return None


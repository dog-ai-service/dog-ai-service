# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from services.make_creds_api import make_creds
# 설정값
from config import TIME_MIN,TIME_MAX,MAX_RESULTS
# http 오류 처리용 
from googleapiclient.errors import HttpError

from datetime import datetime, timedelta


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
    #테스트
    st.info(f"events : {events}")
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
            "event_id" : event.get("id","아이디오류"),
            "calendar_summary" : st.session_state.calendar_list.get(calendar_id, "제목없음"),
            "all_day" : event.get("all_day", True)
        }

        if is_datetime:
            event_data["end"] = end[:16] if end else start[:16]
            event_data["allDay"] = False
        else:
            event_data["allDay"] = True

        calendar_events.append(event_data)
    return calendar_events
''' events 값 예시
[
  {
    "kind": "calendar#event",
    "etag": "3495463972021886",
    "id": "0a3aqb2bflq9st47hnhi08q92h",
    "status": "confirmed",
    "htmlLink": "https://www.google.com/calendar/event?eid=MGEzYXFiMmJmbHE5c3Q0N2huaGkwOHE5MmggMDVkNGQwOTAwNzBiMDUwYzFiYWM4ODc0MWY2OTY2NjgzNTQzMjQ5ZjNjYmU1MzcyN2I1YTZkZjA1MjhlNjJjMkBn",
    "created": "2025-05-20T09:05:14.000Z",
    "updated": "2025-05-20T09:06:26.010Z",
    "summary": "산책",
    "creator": {
      "email": "dhqudwo123@gmail.com"
    },
    "organizer": {
      "email": "05d4d090070b050c1bac88741f6966683543249f3cbe53727b5a6df0528e62c2@group.calendar.google.com",
      "displayName": "두번째 캘린더 테스트",
      "self": true
    },
    "start": {
      "dateTime": "2025-05-07T18:30:00+09:00",
      "timeZone": "Asia/Seoul"
    },
"end": {
    "dateTime": "2025-05-07T19:30:00+09:00",
    "timeZone": "Asia/Seoul"
},
    "iCalUID": "0a3aqb2bflq9st47hnhi08q92h@google.com",
    "sequence": 1,
    "reminders": {
      "useDefault": true
    },
    "eventType": "default"
  },
  {
    "kind": "calendar#event",
    "etag": "3495445135111230",
    "id": "2fnslitesmiji4dkitv9ddtg4v",
    "status": "confirmed",
    "htmlLink": "https://www.google.com/calendar/event?eid=MmZuc2xpdGVzbWlqaTRka2l0djlkZHRnNHYgMDVkNGQwOTAwNzBiMDUwYzFiYWM4ODc0MWY2OTY2NjgzNTQzMjQ5ZjNjYmU1MzcyN2I1YTZkZjA1MjhlNjJjMkBn",
    "created": "2025-05-20T06:29:27.000Z",
    "updated": "2025-05-20T06:29:27.555Z",
    "summary": "두번째 캘런더의 이벤트",
    "creator": {
      "email": "dhqudwo123@gmail.com"
    },
    "organizer": {
      "email": "05d4d090070b050c1bac88741f6966683543249f3cbe53727b5a6df0528e62c2@group.calendar.google.com",
      "displayName": "두번째 캘린더 테스트",
      "self": true
    },
    "start": {
      "date": "2025-05-22"
    },
    "end": {
      "date": "2025-05-23"
    },
    "transparency": "transparent",
    "iCalUID": "2fnslitesmiji4dkitv9ddtg4v@google.com",
    "sequence": 0,
    "reminders": {
      "useDefault": false
    },
    "eventType": "default"
  }
]
'''


# calendar_id의 캘린더 이벤트를 삭제 
def del_calendar_events(event_id, calendar_id='primary'):
    creds = make_creds("calendar")
    
    # 미로그인시 반환
    if not creds:
        st.error("❌ 먼저 로그인하세요")
        return

    # 캘린더 API 서비스 객체 생성
    service = build("calendar", "v3", credentials=creds)
    
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        st.success("✅ 이벤트를 성공적으로 삭제했습니다.")
    except HttpError as error:
        status = error.resp.status
        if status == 404:
            st.error("❌ 이벤트를 찾을 수 없습니다. (404 Not Found)")
        elif status == 403:
            st.warning("⚠️ 해당 캘린더에 대한 권한이 없습니다. (403 Forbidden)")
        else:
            st.error(f"❌ 알 수 없는 오류가 발생했습니다: {error}")

# calendar_id의 캘린더 이벤트를 수정
def update_calendar_events(event_id, summary, description, start_time, end_time, allDay, calendar_id='primary'):
    creds = make_creds("calendar")
    if not creds:
        st.error("❌ 먼저 로그인하세요")
        return

    service = build("calendar", "v3", credentials=creds)

    # Step 1: 기존 이벤트 삭제
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        st.info("🔄 기존 이벤트를 삭제했습니다.")
    except HttpError as error:
        status = error.resp.status
        if status == 404:
            st.warning("⚠️ 기존 이벤트를 찾을 수 없어 삭제하지 못했습니다. 새로 생성만 시도합니다.")
        elif status == 403:
            st.error("❌ 캘린더 권한이 없어 삭제할 수 없습니다.")
            return
        else:
            st.error(f"❌ 이벤트 삭제 중 오류: {error}")
            return

    # Step 2: 새 이벤트 생성
    if allDay:
        # 종일 일정: date 포맷 사용
        if isinstance(start_time, dict):
            start_date_str = start_time.get("date")
        else:
            start_date_str = start_time

        if isinstance(end_time, dict):
            end_date_str = end_time.get("date")
        else:
            end_date_str = end_time

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        event_body = {
            "summary": summary,
            "description": description,
            "start": {"date": start_date.isoformat()},
            "end": {"date": (end_date + timedelta(days=1)).isoformat()}
        }
    else:
        # 시간 포함 일정: dateTime 포맷 사용
        st.info(f"딕 : {start_time}")
        event_body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time["dateTime"][:19], "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end_time["dateTime"][:19], "timeZone": "Asia/Seoul"}
        }

    try:
        new_event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        st.success(f"✅ 이벤트가 새로 생성되었습니다: {new_event.get('summary')}")
    except HttpError as error:
        st.error(f"❌ 이벤트 생성 중 오류 발생: {error}")

# 시간 포맷 변경용
def convert_event_times(event):
    """
    FullCalendar 이벤트 객체에서 start, end 값을
    Google Calendar API에 맞는 포맷(dict)으로 변환
    """
    if event.get("allDay"):
        # 종일 이벤트: 날짜만 필요 ("YYYY-MM-DD")
        start = {"date": event["start"][:10]}
        end = {"date": event["end"][:10]}
    else:
        # 시간 포함 이벤트: dateTime + timeZone 필요
        start = {
            "dateTime": event["start"],
            "timeZone": "Asia/Seoul"
        }
        end = {
            "dateTime": event["end"],
            "timeZone": "Asia/Seoul"
        }
    
    return start, end
    


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


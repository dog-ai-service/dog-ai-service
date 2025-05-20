# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
# 설정값
from config import TIME_MIN,TIME_MAX,MAX_RESULTS




def calendar_api():
    client_id=GOOGLE_CLIENT_ID
    client_secret=GOOGLE_CLIENT_SECRET

    # 세션 상태에 token이 없으면 로그인 버튼 표시
    # 사용할 계정의 Google Calendar API를 사용 상태로 바꾸어야 사용가능
    if "token" not in st.session_state:
        pass
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
        # calendar_list_dict에 캘린더 목록 전부 가져오기
        calendar_list_dict={}
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                # 캘린더 정보 아이디로 딕에 저장
                calendar_list_dict[calendar_list_entry.get('id', '없으면 말이 안되는데...')]=calendar_list_entry
                st.info(calendar_list_entry)
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        calendar_entries = list(calendar_list_dict.values())
        choice = st.radio(
            "캘린더 선택",
            options=calendar_entries,
            format_func=lambda entry: entry.get("summary", "이름이 없으면 말이 안되는데...")
        )

        #테스트
        st.info(choice.get("id","제목없음"))
        # TIME_MIN년부터 가져오기
        time_min = TIME_MIN
        # TIME_MAX년부터 가져오기
        time_max = TIME_MAX
        # 캘린더에서 대충 최신 이벤트 MAX_RESULTS개 가져오기
        events_result = service.events().list(
            calendarId=choice.get("id", '없으면 말이 안되는데...'),
            timeMin=time_min,
            timeMax=time_max,
            maxResults=MAX_RESULTS,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        #테스트
        #st.info(f"calendar_api events : {events}")

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





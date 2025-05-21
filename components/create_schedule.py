import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime
import re
import json
from services.AI.extract_event_info import extract_event_info
from services.AI.schedule_summation import schedule_summation
import pytz
from services.make_creds_api import make_creds



def create_event(start_time, end_time, summary):
    creds = make_creds("calendar")
    if creds:
        # 캘린더 API 서비스 객체 생성
        service = build("calendar", "v3", credentials=creds)
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Seoul',
            },
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        st.success(f'✅ 일정 생성 완료: [{summary}]({event.get("htmlLink")})')

def summation_events():
    creds = make_creds("calendar")
    if creds:
        # 캘린더 API 서비스 객체 생성
        service = build("calendar", "v3", credentials=creds)
    
        seoul = pytz.timezone("Asia/Seoul")
        now = datetime.now(seoul)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        events_processed = []
        for item in events:
            result = {}
            result['title'] = item['summary']
            result['start'] = item['start']['dateTime']
            result['end'] = item['end']['dateTime']
            events_processed.append(result)

        return schedule_summation(events_processed)


def create_schedule():
    prompt = st.text_input("🗣️ 자연어로 일정을 입력하세요: ", 
                           placeholder="시간은 'p.m' 또는 'a.m' 형식으로 입력해주세요. 예) 내일 6 p.m에 강아지 산책")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ 일정 생성"):
            if prompt:
                try:
                    date = datetime.now().strftime('%Y-%m-%d')
                    response = extract_event_info(prompt, date)
                    response_cleaned = re.sub(r'^[^{\[]*', '', response.strip())
                    response_cleaned = response_cleaned.replace("'", '"')
                    event_info = json.loads(response_cleaned)
                    if isinstance(event_info, list):
                        for event in event_info:
                            create_event(event["start"], event["end"], event["summary"])
                    else:
                        create_event(event_info["start"], event_info["end"], event_info["summary"])
                    st.rerun() 
                except Exception as e:
                    st.error(f"❌ 일정 생성 오류: {e}")
            else:
                st.warning("⚠️ 일정을 입력하세요.")

    with col2:
        if st.button("📖 오늘의 일정 요약"):
            events = summation_events()
            if not events:
                st.info("🔎 향후 일정이 없습니다.")
            else:
                st.markdown(events.content)
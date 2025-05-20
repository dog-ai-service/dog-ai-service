import streamlit as st
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import os
from dotenv import load_dotenv
import re
import json
from services.AI.extract_event_info import extract_event_info
from services.AI.summation import summation
import pytz
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_event(start_time, end_time, summary):
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
            scopes=SCOPES
        )
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
            scopes=SCOPES
        )
        # 캘린더 API 서비스 객체 생성
        service = build("calendar", "v3", credentials=creds)
    
        seoul = pytz.timezone("Asia/Seoul")
        now = datetime.now(seoul)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

        events_result = service.events().list(
            #calendarId=os.environ['CALENDAR_ID'],
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

        return summation(events_processed)



def create_schedule():
    prompt = st.text_input("🗣️ 자연어로 일정을 입력하세요:")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ 일정 생성"):
            if prompt:
                date = datetime.now().strftime('%Y-%m-%d')
                response = extract_event_info(prompt, date)
                response_cleaned = re.sub(r'^[^{\[]*', '', response.strip())
                try:
                    event_info = json.loads(response_cleaned)
                    if isinstance(event_info, list):
                        for event in event_info:
                            create_event(event["start"], event["end"], event["summary"])
                    else:
                        create_event(event_info["start"], event_info["end"], event_info["summary"])
                    st.rerun() # 새로 고침
                except Exception as e:
                    st.error(f"❌ 일정 파싱 오류: {e}")
            else:
                st.warning("⚠️ 일정을 입력하세요.")

    with col2:
        if st.button("📖 일정 요약"):
            events = summation_events()
            if not events:
                st.info("🔎 향후 일정이 없습니다.")
            else:
                st.markdown(events.content)
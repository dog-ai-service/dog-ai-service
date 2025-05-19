'''
    캘린더 하단에 일정 생성, 일정 요약을 담당하는 부분
        - 흐름
            - Case 1 : 일정 생성
                - 사용자가 프롬프트에 자연어로 일정 작성
                - 해당 자연어를 extract_event_info를 통해 일정 형식으로 변환(모델을 통해 변환)
                - 변환된 형식을 json으로 바꾸고 calendar에 event 넣음 
            - Case 2 : 일정 요약 
                - summation을 통해 일정 요약 
                - 오늘의 일정 목록을 가공하여 모델에 입력
                - 모델이 일정 요약
'''

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import re
import json
from AI.extract_event_info import extract_event_info
from AI.summation import summation
import pytz

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])



def create_event(start_time, end_time, summary):
    credentials = service_account.Credentials.from_service_account_file(os.environ['SERVICE_ACCOUNT_FILE'], scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
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
    event = service.events().insert(calendarId=os.environ["CALENDAR_ID"], body=event).execute()
    st.success(f'✅ 일정 생성 완료: [{summary}]({event.get("htmlLink")})')

def summation_events():
    credentials = service_account.Credentials.from_service_account_file(os.environ['SERVICE_ACCOUNT_FILE'], scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    
    seoul = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

    events_result = service.events().list(
        calendarId=os.environ['CALENDAR_ID'],
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
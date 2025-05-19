'''
    오늘의 이벤트를 가져오는 함수
'''


from datetime import date
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_today_events():
    credentials = service_account.Credentials.from_service_account_file(
        os.environ['SERVICE_ACCOUNT_FILE'], scopes=SCOPES)
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
    formatted_events = []
    for event in events:
        formatted_events.append({
            "title": event["summary"],
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "end": event["end"].get("dateTime", event["end"].get("date")),
        })
    return formatted_events
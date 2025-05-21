from dateutil import parser
from datetime import timedelta
import streamlit as st

def push_next_only(schedules, calendar_service):
    # 생성된 이벤트 레지스트리 초기화
    if "created_events" not in st.session_state:
        st.session_state.created_events = {}

    for dog in schedules:
        for item in dog["schedule"]:
            key = dog["name"] + ":" + item["type"] + item.get("subtype", "")
            next_dt = item["next"][0]        # 가장 가까운 다음 일정
            end_dt  = calculate_end(item)    # duration 기반 계산

            existing = st.session_state.created_events.get(key)
            if existing:
                # 1) 기존 이벤트가 있으면 start/end만 업데이트
                calendar_service.events().patch(
                    calendarId="primary",
                    eventId=existing["event_id"],
                    body={
                        "start": {"dateTime": next_dt, "timeZone": "Asia/Seoul"},
                        "end":   {"dateTime": end_dt,  "timeZone": "Asia/Seoul"}
                    }
                ).execute()
            else:
                # 2) 없으면 신규 생성
                event = {
                    "summary": f"{dog['name']} — {item['type']}",
                    "start": {"dateTime": next_dt, "timeZone": "Asia/Seoul"},
                    "end":   {"dateTime": end_dt,  "timeZone": "Asia/Seoul"}
                }
                created = calendar_service.events().insert(
                    calendarId="primary", body=event
                ).execute()
                st.session_state.created_events[key] = {
                    "event_id": created["id"]
                }


def calculate_end(item):
    """시작 시간(item['next'][0])에 duration을 더해 종료 시간 계산"""
    start = parser.isoparse(item["next"][0])
    if "duration" in item:
        # ISO 8601 문자열을 parser로 파싱한 뒤 timedelta로 더하기
        # 예시: item["duration"] == "PT20M" → parser.isoparse 불가하므로
        # 간단히 문자열 분석하거나 별도 함수로 처리해야 함
        t_del
        # 여기서는 20분 고정 예시:
        return (start + timedelta(minutes=20)).isoformat()
    # duration이 없으면 기본 30분
    return (start + timedelta(minutes=30)).isoformat()

def build_rrule(period_iso):
    """ISO 8601 period → RRULE 문자열 변환"""
    if period_iso.startswith("P1Y"):
        return "RRULE:FREQ=YEARLY"
    if period_iso.startswith("P") and "D" in period_iso:
        return "RRULE:FREQ=DAILY"
    if period_iso.startswith("PT") and "H" in period_iso:
        return "RRULE:FREQ=HOURLY"
    # 그 외 기본 DAILY
    return "RRULE:FREQ=DAILY"

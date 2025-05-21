import streamlit as st
from dateutil import parser
from datetime import datetime, timedelta
import re

# --- ISO 8601 기간 문자열 파싱용 정규식 (전체 매칭) ---
_iso_duration_pattern = re.compile(
    r'^P'
    r'(?:(?P<years>\d+)Y)?'
    r'(?:(?P<months>\d+)M)?'
    r'(?:(?P<days>\d+)D)?'
    r'(?:T'
    r'(?:(?P<hours>\d+)H)?'
    r'(?:(?P<minutes>\d+)M)?'
    r'(?:(?P<seconds>\d+)S)?'
    r')?$'
)

def parse_iso8601_duration(duration_str: str) -> timedelta:
    """
    ISO 8601 기간 문자열 → datetime.timedelta
    연도는 365일, 월은 30일 기준으로 환산합니다.
    예: "P1Y2M3DT4H5M6S", "PT20M", "P30D"
    """
    match = _iso_duration_pattern.fullmatch(duration_str)
    if not match:
        raise ValueError(f"잘못된 ISO 8601 기간 문자열: {duration_str}")
    parts = {k: int(v) if v else 0 for k, v in match.groupdict().items()}
    total_days = parts['years'] * 365 + parts['months'] * 30 + parts['days']
    return timedelta(days=total_days,
                     hours=parts['hours'],
                     minutes=parts['minutes'],
                     seconds=parts['seconds'])

def add_duration_to_iso(start_iso: str, duration_iso: str) -> str:
    """
    ISO 8601 시작 시각(start_iso) + ISO 8601 기간(duration_iso)
    → 새로운 ISO 8601 시각 문자열 반환
    """
    dt = parser.isoparse(start_iso)
    delta = parse_iso8601_duration(duration_iso)
    return (dt + delta).isoformat()

def calculate_end(item: dict) -> str:
    """
    schedule 항목의 첫 번째 next 시각과 duration을 이용해 종료 시각 계산.
    duration이 없으면 기본 30분(PT30M) 적용.
    """
    start_iso = item["next"][0]
    duration_iso = item.get("duration") or "PT30M"
    return add_duration_to_iso(start_iso, duration_iso)


# --- 한글 & 이모지 매핑 ---
TYPE_KOR = {
    "feeding": "🍖 밥",
    "walking": "🐕 산책",
    "bathing": "🛁 목욕",
    "grooming": "✂️ 미용",
    "heartworm_prevention": "💊 심장사상충",
    "internal_parasite": "💊 내부기생충",
    "vaccination": "💉 예방접종",
}
SUBTYPE_KOR = {
    "DHPPL":          "종합예방주사",
    "rabies":         "광견병",
    "corona":         "코로나장염",
    "kennel_cough":   "켄넬콕스",
}

def make_summary(dog_name: str, item: dict) -> str:
    """
    Google Calendar 이벤트 summary 생성.
    vaccination 타입일 땐 subtype 한글명까지 포함.
    """
    t = item["type"]
    kor = TYPE_KOR.get(t, t)
    if t == "vaccination":
        sub = item.get("subtype", "")
        sub_kor = SUBTYPE_KOR.get(sub, sub.replace("_", " "))
        return f"{dog_name}: {kor}({sub_kor})"
    else:
        return f"{dog_name}: {kor}"


def update_calendar_from_schedules(schedules: list, calendar_service):
    """
    - schedules: [
         {
           "name": str,
           "schedule": [
             {
               "type": ..., "subtype"?: ..., 
               "period": "...", "duration"?: "...", 
               "next": ["...ISO...","..."], ...
             }, ...
           ]
         }, ...
       ]
    - calendar_service: Google Calendar API 서비스 객체
    """
    now = datetime.now()

    # 생성/업데이트된 이벤트 ID 보관 레지스트리
    if "created_events" not in st.session_state:
        st.session_state.created_events = {}  # key: f"{name}:{type}{subtype}:{next_iso}"

    for dog in schedules:
        for item in dog.get("schedule", []):
            updated_next = []

            # 1) 모든 next 시각에 대해 처리 (feeding/walking 같이 여러 번)
            for next_iso in item["next"]:
                key = f"{dog['name']}:{item['type']}{item.get('subtype','')}:{next_iso}"
                start = next_iso
                end   = calculate_end(item)
                summary = make_summary(dog["name"], item)

                event_body = {
                    "summary": summary,
                    "start":   {"dateTime": start, "timeZone": "Asia/Seoul"},
                    "end":     {"dateTime": end,   "timeZone": "Asia/Seoul"},
                }

                # 2) 기존 이벤트가 있으면 patch, 없으면 insert
                if key in st.session_state.created_events:
                    calendar_service.events().patch(
                        calendarId="primary",
                        eventId=st.session_state.created_events[key],
                        body=event_body
                    ).execute()
                else:
                    created = calendar_service.events().insert(
                        calendarId="primary", body=event_body
                    ).execute()
                    st.session_state.created_events[key] = created["id"]

                # 3) 지나간 일정이라면 period만큼 더해 next에 추가
                #    (원하는 경우만 활성화: if parser.isoparse(next_iso) <= now:)
                new_next = add_duration_to_iso(next_iso, item["period"])
                updated_next.append(new_next)

            # 4) item["next"] 전체 갱신
            item["next"] = updated_next

    # 5) 최종 갱신된 schedules를 세션에 저장
    st.session_state.schedules = schedules

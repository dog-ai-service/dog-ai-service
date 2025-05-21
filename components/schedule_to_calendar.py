# schedule_to_calendar.py
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

def calculate_end(start_iso: str, duration_iso: str = None) -> str:
    """
    schedule 항목의 첫 번째 next 시각과 duration을 이용해 종료 시각 계산.
    duration이 없으면 기본 30분(PT30M) 적용.
    """
    dur = duration_iso or "PT30M"
    return add_duration_to_iso(start_iso, dur)


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


def update_calendar_from_schedules(schedules: list, service):
    """
    1) 지난 일정만 period 만큼 밀어서 item['next'] 갱신
    2) 갱신된 next 리스트를 기준으로 캘린더에 insert/patch
    """
    now = datetime.now()

    if "created_events" not in st.session_state:
        st.session_state.created_events = {}

    for dog in schedules:
        for item in dog.get("schedule", []):
            # 1) 지난 일정만 밀어서 next 전체 갱신
            new_next_list = []
            for nxt in item["next"]:
                dt = parser.isoparse(nxt)
                # 지난 일정이면 period 만큼 반복해서 올린다
                while dt < now:
                    nxt = add_duration_to_iso(nxt, item["period"])
                    dt = parser.isoparse(nxt)
                new_next_list.append(nxt)
            item["next"] = new_next_list

            # 2) 갱신된 next들을 캘린더에 푸시
            for nxt in item["next"]:
                key = f"{dog['name']}:{item['type']}{item.get('subtype','')}:{nxt}"
                start = nxt
                end   = calculate_end(start, item.get("duration"))
                body = {
                    "summary":     make_summary(dog["name"], item),
                    "description": item.get("detail", ""),
                    "start":       {"dateTime": start, "timeZone": "Asia/Seoul"},
                    "end":         {"dateTime": end,   "timeZone": "Asia/Seoul"},
                }

                if key in st.session_state.created_events:
                    service.events().patch(
                        calendarId="primary",
                        eventId=st.session_state.created_events[key],
                        body=body
                    ).execute()
                else:
                    created = service.events().insert(
                        calendarId="primary", body=body
                    ).execute()
                    st.session_state.created_events[key] = created["id"]

    # 3) 세션에 최종 반영
    st.session_state.schedules = schedules
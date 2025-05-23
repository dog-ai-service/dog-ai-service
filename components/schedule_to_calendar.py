# schedule_to_calendar.py
import streamlit as st
from dateutil import parser
from datetime import datetime, timedelta
import re
import pytz

# --- ISO 8601 기간 문자열 파싱용 정규식 ---
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
    dt = parser.isoparse(start_iso)
    delta = parse_iso8601_duration(duration_iso)
    return (dt + delta).isoformat()


def calculate_end(start_iso: str, duration_iso: str = None) -> str:
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
    "DHPPL":        "종합예방주사",
    "rabies":       "광견병",
    "corona":       "코로나장염",
    "kennel_cough": "켄넬콕스",
}

# --- 한국시간 전처리 헬퍼 ---
KST = pytz.timezone('Asia/Seoul')

def normalize_to_kst(iso_str: str) -> str:
    dt = parser.isoparse(iso_str)
    dt_naive = dt.replace(tzinfo=None)
    dt_kst = KST.localize(dt_naive)
    return dt_kst.isoformat()

# --- 이벤트 summary 생성 ---
def make_summary(dog_name: str, item: dict) -> str:
    t = item["type"]
    kor = TYPE_KOR.get(t, t)
    if t == "vaccination":
        sub = item.get("subtype", "")
        sub_kor = SUBTYPE_KOR.get(sub, sub.replace("_", " "))
        return f"{dog_name}: {kor}({sub_kor})"
    return f"{dog_name}: {kor}"

# --- 캘린더 업데이트 ---
def update_calendar_from_schedules(schedules: list, service):
    now = datetime.now(KST)
    # 초기화: created_events가 없으면 빈 리스트로
    if "created_events" not in st.session_state:
        st.session_state.created_events = []

    for dog in schedules:
        # 해당 강아지 entry 찾기 또는 생성
        entry = next((e for e in st.session_state.created_events if e.get("name") == dog["name"]), None)
        if entry is None:
            entry = {"name": dog["name"], "events": []}
            st.session_state.created_events.append(entry)
        events_list = entry["events"]  # list of dicts

        for item in dog.get("schedule", []):
            # next를 리스트로 통일하고 시간 변환
            nxts = item.get("next")
            if isinstance(nxts, str):
                nxts = [nxts]
            item["next"] = [normalize_to_kst(x) for x in nxts]

            # 지난 일정 업데이트
            new_next = []
            for nxt in item["next"]:
                dt = parser.isoparse(nxt)
                while dt < now:
                    nxt = add_duration_to_iso(nxt, item["period"])
                    dt = parser.isoparse(nxt)
                new_next.append(nxt)
            item["next"] = new_next

            # 이벤트 삽입/수정: index 기반 key 생성
            for idx, start in enumerate(item["next"]):
                key = f"{dog['name']}:{item['type']}{item.get('subtype','')}:{idx}"
                end = calculate_end(start, item.get("duration"))
                body = {
                    "summary": make_summary(dog['name'], item),
                    "description": item.get("detail", ""),
                    "start": {"dateTime": start, "timeZone": "Asia/Seoul"},
                    "end": {"dateTime": end, "timeZone": "Asia/Seoul"},
                }
                existing = next((ev for ev in events_list if key in ev), None)
                if existing:
                    event_id = existing[key]
                    service.events().patch(
                        calendarId="primary",
                        eventId=event_id,
                        body=body
                    ).execute()
                else:
                    created = service.events().insert(
                        calendarId="primary", body=body
                    ).execute()
                    events_list.append({key: created.get("id")})

    # schedules 저장
    st.session_state.schedules = schedules
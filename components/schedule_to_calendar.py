# schedule_to_calendar.py (업데이트)
import streamlit as st
from dateutil import parser
from datetime import datetime, timedelta
import re
import pytz

# --- ISO 8601 기간 문자열 Parsing 정규식 ---
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

# --- Duration Parser ---
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

# --- ISO 시작 시각 + 기간 = 종료 시각 ---
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

# --- 한국시간 전처리 헬퍼 (Z를 로컬 시각으로 해석) ---
KST = pytz.timezone('Asia/Seoul')

def normalize_to_kst(iso_str: str) -> str:
    """
    '2025-06-22T00:00:00Z' 등을 로컬 시간 그대로 유지하며
    Asia/Seoul(+09:00) 타임존을 붙여 반환합니다.
    """
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
    cal_id = "primary"

    if 'created_events' not in st.session_state or not isinstance(st.session_state.created_events, dict):
        st.session_state.created_events = {}

    # next 필드 일관화 (단일 문자열 + Z 표기 처리)
    for dog in schedules:
        for item in dog.get("schedule", []):
            nxts = item.get("next")
            if isinstance(nxts, str):
                nxts = [nxts]
            nxts = [normalize_to_kst(x) for x in nxts]
            item["next"] = nxts

    # 이벤트 body 생성
    def create_event_body(dog, item, start_iso):
        return {
            "summary": make_summary(dog["name"], item),
            "description": item.get("detail", ""),
            "start": {"dateTime": start_iso, "timeZone": "Asia/Seoul"},
            "end": {"dateTime": calculate_end(start_iso, item.get("duration")), "timeZone": "Asia/Seoul"},
            "extendedProperties": {"shared": {"source": "dog-schedule-app"}}
        }

    # 이벤트 insert/patch
    for dog in schedules:
        for item in dog.get("schedule", []):
            for start_iso in item["next"]:
                key = f"{dog['name']}:{item['type']}{item.get('subtype','')}:{start_iso}"
                body = create_event_body(dog, item, start_iso)
                if key in st.session_state.created_events:
                    eid = st.session_state.created_events[key]
                    service.events().patch(calendarId=cal_id, eventId=eid, body=body).execute()
                else:
                    created = service.events().insert(calendarId=cal_id, body=body).execute()
                    st.session_state.created_events[key] = created.get("id")

    st.session_state.schedules = schedules
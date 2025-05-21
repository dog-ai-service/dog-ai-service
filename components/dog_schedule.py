import streamlit as st
import json
from openai import OpenAI
from datetime import date
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE, OPENAI_API_KEY
from services.calendar_api import get_calendar_service
from components.schedule_to_calendar import update_calendar_from_schedules

# 오늘 날짜 (ISO-8601)
today = date.today().isoformat()

# OpenAI 클라이언트
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = f"""
당신은 반려견 케어 스케줄 어시스턴트입니다. 오늘 날짜: {today}.
입력: JSON dogs 배열 — 각 요소: name, breed, birth, de_sex, weight, note
출력: JSON 배열 예시 —
[
  {{
    name,
    schedule: [
      {{
        type,             # feeding, walking, bathing, grooming, heartworm_prevention, internal_parasite, vaccination
        subtype?,         # (vaccination만) DHPPL, rabies, corona, kennel_cough
        period,           # 다음 반복까지 ISO 8601 기간
        duration?,        # 활동 소요 ISO 8601 기간
        count?,           # 반복 횟수 (feeding, walking만)
        detail?,          # 추가 메모
        next              # ISO 8601 타임스탬프 리스트
      }}
    ]
  }}
]

규칙:
- feeding: period=P1D
  • 소·중형(≤25kg): count=2, duration=PT15M  
    → next 시각: **하루 2회**, 보통 **08:00**과 **20:00**에 설정  
  • 대형(>25kg):     count=2, duration=PT30M  
    → next 시각: **07:00**, **19:00**  
  • 비만 or note “급하게 먹음”: duration=PT20M, count+=1  
    → 아침(08:00), 점심(12:00), 저녁(20:00) 등 적절히 배분  
- walking: period=P1D
  • 소·중형: count=2, duration=PT20M  
    → next 시각: **10:00**과 **18:00**  
  • 대형:     count=1,  duration=PT60M  
    → 다음 산책 시각: **17:00**  
  • 과체중: count+=1; 관절문제→duration=PT10M  
    → 추가 산책은 **15:00** 등  
- bathing: period=P14D  (건조→P21D(저자극 샴푸권장), 지성→P7D)  
  → 주말 오전(10:00) 또는 주말 저녁(18:00)  
- grooming: period=P60D  
  → 평일 18:00  
- heartworm_prevention: period=P1M  
  → 주말 오후(14:00)  
- internal_parasite:
  • 생후 ≤6개월: period=P1M  
    → 주말 오후(14:00)  
  • 이후:         period=P3M
- vaccination: 다음 네 개 항목을 각각 schedule에 모두 포함할 것:
  - {{type: "vaccination", subtype:"DHPPL", period:"P1Y"}}
  - {{type: "vaccination", subtype:"rabies", period:"P1Y"}}
  - {{type: "vaccination", subtype:"corona", period:"P1Y"}}
  - {{type: "vaccination", subtype:"kennel_cough", period:"P1Y"}}
• 각각의 next:
  - “올해 생일 월”의 주말 오후(14:00)에 설정  
  - (만약 오늘이 생일 월을 지났으면 내년 생일 월 사용)
- 필드 해설:
  period=다음 간격, duration=소요 시간,  
  next=예정 시각 리스트(feeding/walking은 위 지정 시간, 그 외는 평일 퇴근 후·주말 오후 시간대),  
  detail=특이사항 기입(저자극 샴푸권장 등)  
반환: 오직 JSON — 부가 설명 금지
"""



def fetch_personalized_schedule(dogs):
    system_msg = {"role":"system","content":SYSTEM_PROMPT}
    user_msg   = {"role":"user","content":json.dumps(
        {"dogs":[
            {k: (v.isoformat() if hasattr(v, "isoformat") else v)
             for k,v in {
                "name":   d["name"],
                "breed":  d["breed"],
                "birth":  d["birth"],
                "de_sex": d["de_sex"],
                "weight": d["weight"],
                "note":   d["note"],
            }.items()}
            for d in dogs
        ]}, ensure_ascii=False
    )}
    resp = client.chat.completions.create(
        model=OPENAI_API_MODEL,
        messages=[system_msg, user_msg],
        temperature=0.2
    )
    raw = resp.choices[0].message.content or ""
    
    # 1) 응답이 비어있는지 체크
    if not raw.strip():
        st.error("모델 응답이 비어있습니다.")
        return []
    
    # 2) 디버그용 전체 응답 출력
    st.text_area("🔍 모델 원본 응답", raw, height=200)

    # 3) JSON 파싱 시도
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 오류: {e}")
        return []

# Streamlit 버튼 핸들러
def dog_scheduling():
    service = get_calendar_service()
    if not service:
        return  # 서비스 생성 실패 시 중단
    # 세션 초기화
    if "schedules" not in st.session_state:
        st.session_state.schedules = []
    if "created_events" not in st.session_state:
        st.session_state.created_events = {}

    if st.button("1️⃣ 개인화 케어 스케줄 생성"):
        dogs = st.session_state.get("dogs", [])
        if not dogs:
            st.warning("먼저 강아지를 등록해주세요.")
            return
        
        # 1) 이전 스케줄 보관
        old_schedules = st.session_state.get("schedules", [])

        # 2) LLM 호출
        with st.spinner("생성 중…"):
            new_schedules = fetch_personalized_schedule(dogs)

        # 3) 이전 next 값 재활용 로직
        # old_schedules/new_schedules 는 [{ "name":…, "schedule":[…] }, …] 구조
        # 각 항목을 dog 이름 + schedule 타입(key) 으로 매핑해 두면 빠릅니다.
        old_map = {}
        for dog in old_schedules:
            for item in dog["schedule"]:
                key = dog["name"] + ":" + item["type"] + item.get("subtype", "")
                old_map[key] = item

        # 병합
        for dog in new_schedules:
            for item in dog["schedule"]:
                key = dog["name"] + ":" + item["type"] + item.get("subtype", "")
                old_item = old_map.get(key)
                # period 동일 → next 재활용
                if old_item and old_item.get("period") == item.get("period"):
                    item["next"] = old_item["next"]

        # 4) 재활용 후 최종 저장
        st.session_state.schedules = new_schedules
        # print(f"스케줄 타입: {type(st.session_state.schedules)}")
        # print(f"스케줄 내용: {st.session_state.schedules}")

    # 2️⃣ 캘린더 동기화
    if st.button("2️⃣ 캘린더 업데이트"):
        if not st.session_state.schedules:
            st.error("먼저 스케줄을 생성해주세요.")
        else:
            update_calendar_from_schedules(st.session_state.schedules, service)
            st.success("캘린더가 동기화되었습니다.")

    # 스케줄 출력
    st.subheader("🗓️ 현재 스케줄")
    schedules = st.session_state.get("schedules", [])
    if not schedules:
        st.info("아직 생성된 스케줄이 없습니다.")
    else:
        st.json(schedules)

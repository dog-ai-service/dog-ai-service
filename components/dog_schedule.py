import streamlit as st
import json
from openai import OpenAI
from datetime import date
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE, OPENAI_API_KEY
from services.calendar_api import get_calendar_service
from components.schedule_to_calendar import push_next_only

# 오늘 날짜 (ISO-8601)
today = date.today().isoformat()

# OpenAI 클라이언트
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = f"""
당신은 반려견 맞춤 케어 스케줄링 어시스턴트입니다.  
오늘 날짜는 {today} 입니다.

아래 JSON으로 주어진 강아지 정보(name, breed, birth, de_sex, weight, note)를  
다음 **근거 기반** 가이드라인에 따라 **개인화** 스케줄을 생성하세요.

=== 1. 식사(feeding) ===  
• 성견 일반: 하루 2회, 8–12시간 간격으로 급여(Adult dogs: 2×/day at 8–12 h intervals)
• 소형견(<10 kg): 2회/일  
• 중형견(10–25 kg): 2회/일  
• 대형견(>25 kg): 2–3회/일 
• 비만(ideal_weight+10%↑): feed_period→8 h, 1회량 –20%, 횟수↑   
• note에 “급하게 먹음” 포함 시 1회량 –30%, 횟수 +50%

=== 2. 산책(walking) ===  
• 대부분 성견: 매일 20–30 분 산책 (moderate)
• 또는 하루 3–4회×15 분
• 소형견: 짧고 잦은 산책, 20 분×2 회  
• 중형견: 30 분×2 회  
• 대형견: 60 분×1 회 또는 30 분×2 회  
• 과체중 시 주당 +1회 산책  
• note에 “슬개골”, “관절통” 등 관절문제 시 low-impact, 자주 / 짧게

=== 3. 목욕(bathing) & 미용(grooming) ===  
• 일반: 목욕 1 개월(≈30 일)·미용 2 개월(≈60 일)  
• 소형견: bath 8 주, medium-coat 장모견: 6 주, 대형견·장모견: 4 주  
• note에 “피부” 관련(알러지·건조) 시 bath_period→14 일, 저자극 샴푸 권장

=== 4. 심장사상충 예방 ===  
- 모든 반려견은 **매월 1회** 심장사상충 예방 약(구충제) 투여가 권장됩니다.  
- 성견(7개월 이상) 또는 6개월 이상 예방 간격이 있을 경우 **투여 전 1회 항원 검사**를 반드시 수행하세요.  

=== 5. 내부 기생충 예방 ===  
- 생후 **6개월까지 매월 1회**, 그 이후에는 최소 **3개월마다 1회** 구충 치료를 권장합니다.  

=== 6. 기타 예방접종 (other_vaccinations) ===  
- **종합예방주사 (DHPPL)**  
  • 기초: 생후 6–8주 1차 → 2–4주 간격 추가 1–2회  
  • 보강: 매년 1회  
- **코로나바이러스성 장염 예방**  
  • 기초: 생후 6–8주 1차 → 2–4주 간격 추가 1–2회  
  • 보강: 매년 1회  
- **기관·기관지염 (Kennel Cough)**  
  • 기초: 생후 6–8주 1차 → 2–4주 간격 추가 1–2회  
  • 보강: 매년 1회  
- **광견병 (Rabies)**  
  • 기초: 생후 3개월 이상 1회  
  • 보강: 첫 접종 6개월 후 1회 → 그 뒤 매년 1회

심장사상충 예방, 내부 기생충 예방, 기타 예방접종의 각각의 일정들은 같은 월에 진행하는 경우, 되도록 모두 같은 날에 진행한다.

모든 `"period"`는 **다음 반복 일정까지의 간격**을 나타내는 ISO 8601 기간 문자열이어야 하고,  
필요 시 **지속시간(duration)** 은 별도 `duration` 필드에 ISO 8601 기간 문자열로 정의하세요.  

• `next` 배열 값은 ISO 8601 형식의 타임스탬프로,  
  – feeding·walking은 하루 `count` 횟수만큼,  
  – 그 외는 한 번씩 반환  
• JSON 결과만, 불필요한 설명 없이 반환
=== 7. 출력 예시 ===  
[
  {{
    "name": "청이",
    "schedule": [
      {{
        "type": "feeding",
        "period": "PT12H",
        "duration": "PT15M",
        "count": 2,
        "next": ["2025-05-21T08:00:00", "2025-05-21T20:00:00"]
      }},
      {{
        "type": "walking",
        "period": "PT12H",
        "duration": "PT20M",
        "count": 2,
        "next": ["2025-05-21T10:00:00", "2025-05-21T22:00:00"]
      }},
      {{
        "type": "bathing",
        "period": "P30D",
        "next": ["2025-06-19T10:00:00"]
      }},
      {{
        "type": "grooming",
        "period": "P60D",
        "next": ["2025-07-19T10:00:00"]
      }},
      {{
        "type": "heartworm_prevention",
        "period": "P1M",
        "next": ["2025-06-20T10:00:00"]
      }},
      {{
        "type": "internal_parasite",
        "period": "P3M",
        "next": ["2025-08-20T10:00:00"]
      }},
      {{
        "type": "vaccination",
        "subtype": "DHPPL",
        "period": "P1Y",
        "next": ["2025-11-22T10:00:00"]
      }},
      {{
        "type": "vaccination",
        "subtype": "rabies",
        "period": "P1Y",
        "next": ["2025-11-24T10:00:00"]
      }},
      {{
        "type": "vaccination",
        "subtype": "corona",
        "period": "P1Y",
        "next": ["2025-11-22T10:00:00"]
      }},
      {{
        "type": "vaccination",
        "subtype": "kennel_cough",
        "period": "P1Y",
        "next": ["2025-11-22T10:00:00"]
      }}
    ]
  }}
]"""

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

# Streamlit 버튼 핸들러 예시
def dog_scheduling():
    service = get_calendar_service()
    if not service:
        return  # 서비스 생성 실패 시 중단
    if st.button("개인화 케어 스케줄 생성"):
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

        push_next_only(new_schedules, service)

    # 화면에 JSON 표시
    if sched := st.session_state.get("schedules"):
        st.json(sched)

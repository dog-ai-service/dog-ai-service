import streamlit as st
import json
from openai import OpenAI
from datetime import date
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE, OPENAI_API_KEY
from services.calendar_api import get_calendar_service
from components.schedule_to_calendar import update_calendar_from_schedules
from components.retrieve_guidelines import retrieve_guidelines

# 오늘 날짜 (ISO-8601)
today = date.today().isoformat()

# OpenAI 클라이언트
client = OpenAI(api_key=OPENAI_API_KEY)

# 스케줄 생성 모듈
def fetch_personalized_schedule(dogs, rag_contexts):
    """
    dogs: [{…}, …]
    rag_contexts: { topic: "…", … }
    """
    results = []
    today = date.today().isoformat()

    # 사전 정의
    TOPICS = [
        "feeding",
        "walking",
        "bathing",
        "grooming",
        "heartworm_prevention",
        "internal_parasite",
        "vaccination",
    ]

    for dog in dogs:
        partials = []
        for topic in TOPICS:
            system_prompt = f"""
            You are a professional canine care scheduling assistant.
            Today is {today}.
            Generate only one JSON object for the '{topic}' schedule for the following dog.
            Use the RAG context below to ensure accuracy.

            RAG CONTEXT for {topic}:
            {rag_contexts[topic]}

            Dog data: {json.dumps(dog, ensure_ascii=False)}

            Return a JSON object with exactly these keys:
            - type: string
            - period: ISO 8601 interval
            - duration (optional)
            - count (optional)
            - next: list of ISO 8601 timestamps
            - detail: string (in Korean)

            Return _only_ the JSON object.
            """.strip()

            resp = client.chat.completions.create(
                model=OPENAI_API_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ""},  
                ],
                temperature=0.2,
            )
            item = json.loads(resp.choices[0].message.content)
            partials.append(item)

        results.append({
            "name": dog["name"],
            "schedule": partials
        })

    return results

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
        # RAG 컨텍스트 생성
        rag_contexts = {
            topic: "\n\n".join(retrieve_guidelines(topic, top_k=3))
            for topic in ["feeding", "walking", "bathing", "grooming", "heartworm_prevention", "internal_parasite", "vaccination"]
        }
        # 1) 이전 스케줄 보관
        old_schedules = st.session_state.get("schedules", [])

        # 2) LLM 호출
        with st.spinner("생성 중…"):
            new_schedules = fetch_personalized_schedule(dogs, rag_contexts)

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

import streamlit as st
import json
import re
import textwrap
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

# 강아지 데이터 전처리
def make_serializable(d: dict) -> dict:
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in d.items()}

# 코드블록 제거 및 JSON 추출
def strip_codeblock(s: str) -> str:
    text = re.sub(r"```(?:json)?\s*([\s\S]*?)```", r"\1", s).strip()
    m = re.search(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL)
    return m.group(1) if m else text

# 스케줄 생성 모듈
def fetch_personalized_schedule(dogs, rag_contexts):
    results = []
    today_iso = date.today().isoformat()

    TOPICS = [
        "feeding", "walking", "bathing", "grooming",
        "internal_parasite", "vaccination",
    ]

    for dog in dogs:
        partials = []
        dog_for_prompt = make_serializable(dog)

        for topic in TOPICS:
            system_prompt = textwrap.dedent(f"""
                You are a professional canine care scheduling assistant.
                Today is {today_iso}.
                Generate only one JSON object for the '{topic}' schedule for the following dog.
                Use the RAG context below to ensure accuracy.

                RAG CONTEXT for {topic}:
                {rag_contexts[topic]}

                Dog data: {json.dumps(dog_for_prompt, ensure_ascii=False, default=lambda o: o.isoformat() if hasattr(o, 'isoformat') else str(o))}

                Return a JSON object with exactly these keys:
                - type: string, {topic}
                - period: ISO 8601 interval (e.g. P1D(once a day), P14D(once every 14 days), P1M(once a month), P1Y(once a year), ...). Do NOT use date ranges here.
                - next:
                  • If period == P1D (daily topics: feeding, walking), then list every timestamp **within the next day**.
                  • If type == "vaccination": extract the birth month and day from Dog data["birth"], then format next as an ISO 8601 timestamp “YYYY-MM-DDT00:00:00Z” using the current year if that date is on or after Today, otherwise use the same month/day in the next year.
                  • Otherwise (period is P1M or longer), list exactly **one** ISO 8601 timestamp (the very next occurrence).
                - detail: Korean description string.

                Only output the raw JSON object—no surrounding text or markdown.
                Return only the JSON object without any explanation.
            """).strip()

            resp = client.chat.completions.create(
                model=OPENAI_API_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ""},
                ],
                temperature=0.2,
            )

            raw = resp.choices[0].message.content or ""
            # st.text_area("🔍 Raw Response", raw, height=200)
            if not raw.strip():
                # st.error(f"[{dog['name']}/{topic}] 모델 응답이 비어있습니다.")
                continue

            clean = strip_codeblock(raw)
            try:
                item = json.loads(clean)
            except json.JSONDecodeError as e:
                # st.error(f"[{dog['name']}/{topic}] JSON 파싱 오류: {e}")
                continue

            partials.append(item)

        results.append({"name": dog["name"], "schedule": partials})

    return results

# Streamlit 버튼 핸들러
def dog_scheduling():
    service = get_calendar_service()
    if not service:
        return

    if "schedules" not in st.session_state:
        st.session_state.schedules = []
    if "created_events" not in st.session_state:
        st.session_state.created_events = {}

    if st.button("1️⃣ 개인화 케어 스케줄 생성"):
        dogs = st.session_state.get("dogs", [])
        if not dogs:
            st.warning("먼저 강아지를 등록해주세요.")
            return

        # RAG 컨텍스트 준비
        rag_contexts = {topic: "\n\n".join(retrieve_guidelines(topic, top_k=2))
                        for topic in ["feeding", "walking", "bathing", "grooming", 
                                      "heartworm_prevention", "internal_parasite", "vaccination"]}

        old_schedules = st.session_state.schedules
        with st.spinner("생성 중…"):
            new_schedules = fetch_personalized_schedule(dogs, rag_contexts)

        # 이전 next 재활용
        old_map = {}
        for d in old_schedules:
            for itm in d.get("schedule", []):
                key = d["name"] + ":" + itm.get("type", "") + itm.get("subtype", "")
                old_map[key] = itm

        for d in new_schedules:
            for itm in d.get("schedule", []):
                key = d["name"] + ":" + itm.get("type", "") + itm.get("subtype", "")
                old = old_map.get(key)
                if old and old.get("period") == itm.get("period"):
                    itm["next"] = old["next"]

        st.session_state.schedules = new_schedules

    if st.button("2️⃣ 캘린더 업데이트"):
        if not st.session_state.schedules:
            st.error("먼저 스케줄을 생성해주세요.")
        else:
            update_calendar_from_schedules(st.session_state.schedules, service)
            st.success("캘린더가 동기화되었습니다.")

    # st.subheader("🗓️ 현재 스케줄")
    # if not st.session_state.schedules:
    #     st.info("아직 생성된 스케줄이 없습니다.")
    # else:
    #     st.json(st.session_state.schedules)

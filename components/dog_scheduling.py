import streamlit as st
import json
from openai import OpenAI
from datetime import date
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE, OPENAI_API_KEY
import wikipedia

# 1) Instantiate the new client
client = OpenAI(api_key=OPENAI_API_KEY)
today = date.today().isoformat()

def fetch_wiki_summary(topic: str, sentences: int = 3) -> str:
    """Wikipedia API로부터 topic 요약 본을 반환"""
    try:
        return wikipedia.summary(topic, sentences=sentences)
    except Exception as e:
        st.error(f"Wikipedia 검색 실패: {e}")
        return ""

# 2) Your system prompt

SYSTEM_PROMPT = f"""
You are a scheduling assistant. Today is {today}.  
Given a list of dogs with their info (name, breed, birth date, neuter status, weight, note), 
output a JSON array where each element has these fields:

- name
- feed_period: e.g. "12 hours"
- feed_next: next recommended feeding date-time (ISO 8601, any day/time on or after {today})
- walk_period: e.g. "24 hours"
- walk_next: next recommended walk date-time (ISO 8601, any day/time on or after {today})
- bath_period: e.g. "30 days"
- bath_next: next recommended bath date-time (ISO 8601, must fall on a Saturday or Sunday)
- groom_period: e.g. "60 days"
- groom_next: next recommended grooming date-time (ISO 8601, Saturday or Sunday)
- heartworm_period: e.g. "6 months"
- heartworm_next: next recommended heartworm prevention date-time (ISO 8601, Saturday or Sunday)
- parasite_period: e.g. "3 months"
- parasite_next: next recommended parasite prevention date-time (ISO 8601, Saturday or Sunday)
- other_vaccinations: list of objects with:
    - type: vaccine name
    - period: e.g. "1 year"
    - next: next recommended date-time (ISO 8601, Saturday or Sunday)

Return **only** the raw JSON array, no extra text.
"""

def fetch_schedules_from_llm(dogs):
    vaccine_guide = fetch_wiki_summary("Vaccination of dogs", sentences=5)
    # build messages
    system_msg = {"role": "system", "content": SYSTEM_PROMPT}
    payload_dogs = []
    for d in dogs:
        payload_dogs.append({
            "name":   d["name"],
            "breed":  d["breed"],
            "gender": d["gender"],
            "de_sex": d["de_sex"],
            "birth":  d["birth"].isoformat(),   # YYYY-MM-DD
            "weight": d["weight"],
            "note":   d["note"],
        })

    user_content = json.dumps(
        {"dogs": payload_dogs},
        ensure_ascii=False
    )

    # 2) 실제 보내는 메시지
    system_msg = {"role": "system", "content": SYSTEM_PROMPT}
    user_msg   = {"role": "user",   "content": user_content}

    # **디버그용**: 여기서 JSON 문자열을 확인!
    st.text_area("📦 Payload (JSON)", user_content, height=200)

    # 3) Call the new SDK interface
    resp = client.chat.completions.create(
        model=OPENAI_API_MODEL,
        messages=[system_msg, user_msg],
        temperature=0.2,
    )

    text = resp.choices[0].message.content
    return text

# Usage in Streamlit page
def dog_scheduling():
    dogs = st.session_state.get("dogs", [])
    schedules = fetch_schedules_from_llm(dogs)
    st.session_state.schedules = schedules

    if schedules := st.session_state.get("schedules"):
        st.markdown('---')
        st.markdown('📅 생성된 스케줄')
        st.write(st.session_state.schedules)
    print(st.session_state.schedules)


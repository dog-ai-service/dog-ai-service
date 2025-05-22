import streamlit as st
import re
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from llama_index.core import StorageContext, load_index_from_storage
from deep_translator import GoogleTranslator
from services.AI.make_health_note import make_health_note
from services.drive_healthnote_api import sheet_write, get_sheet_id

def symptom_chatbot(name):
    # 1) 세션에 전용 챗봇 기록 구조 초기화
    #    [{"name": "...", "chat_history": [{"type":..., "content":...}, ...]}, ...]
    if "symptom_chat_history" not in st.session_state:
        st.session_state.symptom_chat_history = []

    # 2) 해당 강아지(name)에 해당하는 기록 객체 찾기 (또는 새로 생성)
    record = next((rec for rec in st.session_state.symptom_chat_history if rec["name"] == name), None)
    if record is None:
        record = {"name": name, "chat_history": []}
        st.session_state.symptom_chat_history.append(record)

    # 3) StreamlitChatMessageHistory 객체 생성
    history = StreamlitChatMessageHistory()

    # 4) 해당 강아지의 과거 대화 렌더링 & history 객체에 적재
    for msg in record["chat_history"]:
        role, content = msg["type"], msg["content"]
        st.chat_message(role).write(content)
        if role == "user":
            history.add_user_message(content)
        else:
            history.add_ai_message(content)

    # 5) 사용자 입력 처리
    prompt = st.chat_input(f"{name}의 증상을 자세히 입력해주세요.")
    if not prompt:
        return

    # 5-1) 유저 메시지 출력 및 기록
    with st.chat_message("user"):
        st.markdown(prompt)
    history.add_user_message(prompt)
    record["chat_history"].append({"type": "user", "content": prompt})

    # 6) AI 응답 생성: 번역 → LlamaIndex 쿼리 → 재번역
    translated_prompt = GoogleTranslator(source="auto", target="en").translate(prompt)
    formatted = f'''
{translated_prompt}
Tell me three suspected symptoms.
Also, explain each symptom in detail.
Please respond in the format below.
And explain how to deal with each symptom.

<Example>
1. Heart disease: Heart disease is a common cardiac valve disease in dogs that can lead to issues like gasping, lack of energy, and coughing. It is important to conduct regular heart tests to prevent this condition.
'''
    with st.spinner("AI가 질병을 분석하고 있어요..."):
        ctx = StorageContext.from_defaults(persist_dir='index_db_backup')
        idx = load_index_from_storage(ctx)
        eng_res = idx.as_query_engine().query(formatted).response

    parts = re.findall(r"\d+\..*?(?=\n\d+\.|\Z)", eng_res, flags=re.DOTALL)
    ko_parts = [GoogleTranslator(source='en', target='ko').translate(p.strip()) for p in parts]
    ko_response = "### 🩺 예측해볼 수 있는 질병들\n\n" + "\n\n".join(ko_parts) + "\n\n> #### 🔎 자세한 상담은 반드시 수의사와 진행하시길 바랍니다."

    # 7) AI 메시지 출력 및 기록
    with st.chat_message("assistant"):
        st.markdown(ko_response)
    history.add_ai_message(ko_response)
    record["chat_history"].append({"type": "assistant", "content": ko_response})

    # 8) 건강 노트 시트 기록
    with st.spinner("강아지 건강 정보를 기입중입니다..."):
        try:
            info = make_health_note(prompt)
            names = re.findall(r"\d+\.\s*([^:]+?)\s*:", ko_response)
            info['의심 질병'] = ", ".join(names)
            if sheet_write(get_sheet_id(name), [info]) is not None:
                st.success("기입 완료!")
        except:
            empty = {'날짜':'', '주요 증상':'', '의심 질병':'', '필요한 조치':'', '추가 메모':''}
            if sheet_write(get_sheet_id(name), [empty]) is not None:
                st.success("기입 완료!")

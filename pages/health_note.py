import streamlit as st
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from datetime import date
#사이드바 로그인
from components.sidebar import sidebar


def health_note():
    st.title("🐶 강아지 헬스 노트 자동 작성기")

    # 예시: chatbot.py에서 전달한 증상 텍스트를 가져오는 세션 상태
    if "symptom_prompt" in st.session_state:
        prompt = st.session_state.symptom_prompt
        make_health_note(prompt)


def make_health_note(prompt):
    llm = ChatOpenAI(
        model_name=os.environ['OPENAI_API_MODEL'],
        temperature=float(os.environ['OPENAI_API_TEMPERATURE'])
    )

    health_note_prompt = f"""
    사용자가 입력한 강아지의 증상:
    "{prompt}"

    위 내용을 기반으로 다음 형식에 맞춰 강아지의 건강 상태를 정리해줘.

    <작성 형식 예시>
    🐾 강아지 헬스 노트
    1. 주요 증상: 구토, 설사
    2. 의심 질병: 장염, 식중독
    3. 보호자에게 필요한 조치: 수분 섭취, 금식, 병원 방문 권장
    4. 추가 메모: 하루 이상 지속 시 즉시 병원 방문 권장

    위의 예시와 유사한 포맷으로 정리해줘.
    """

    res = llm.invoke([HumanMessage(content=health_note_prompt)])

    today = date.today().isoformat()
    st.subheader(f"📋 자동 생성된 헬스 노트 {today}")
    st.markdown(res.content)

    st.session_state.health_note_result = res.content


# 사이드바 렌더링
sidebar()
# 페이지 함수 실행
health_note()

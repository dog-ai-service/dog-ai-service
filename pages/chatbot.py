
from components.prompt_box import prompt_box
from components.symptom_chatbot import symptom_chatbot


import streamlit as st
#사이드바 로그인
from components.sidebar import sidebar
sidebar()

st.title("💬 강아지 증상 전문 챗봇")


# 토글버튼을 통해 증상 챗봇 활성화/비활성화 -> 활성화면 증상 전문 챗봇 , 활성화되지 않으면 일상 챗봇 
# 최대한 오른쪽에 배치
st.toggle("증상 챗봇 활성화", value=False, key="symptom_chatbot")
if st.session_state.symptom_chatbot:
    try:
        names = []
        for item in st.session_state.dogs:
            names.append(item['name'])
    except:
        st.error("❌ user_page에서 강아지 정보를 먼저 기입하세요!")
    name = st.selectbox(
     '어떤 강아지의 증상인가요?',
     names,
     index=None,
     placeholder="선택해주세요",
    )
    if name:
        symptom_chatbot()
else:
    prompt_box()

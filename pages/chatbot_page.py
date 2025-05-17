# ui
import streamlit as st
# 프롬프트
from components.prompt_box import prompt_box

def chatbot_page():
    # 채팅 입력창
        # 로그인한 사용자만 아래 실행
        if "token" in st.session_state:
            #프롬프트
            prompt_box()
        else :
            st.title("사용자 정보에서 로그인하세요")

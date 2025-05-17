# 모듈가져오기
# ui
import streamlit as st
# 컴포넌트
from components.sidebar import sidebar
from components.prompt_box import prompt_box
# 서비스
from services.login_api import login_api

def init_chat():
    # 제목
    st.title("LLM, 랭체인, Streamlit 기반 서비스")
    # sidebar
    sidebar()
    # 로그인
    login_api()
    # 채팅 입력창
    # 로그인한 사용자만 아래 실행
    if "token" in st.session_state:
        #프롬프트
        prompt_box()

def main():
    init_chat()

# 프로그램 가동
if __name__ == '__main__':
    main()